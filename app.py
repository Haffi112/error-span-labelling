import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql.expression import func
from flask import send_file
import csv
from io import StringIO
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_wtf.file import FileField, FileRequired, FileAllowed
import random

# Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class CSVUploadForm(FlaskForm):
    file = FileField('CSV File', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV files only!')
    ])
    submit = SubmitField('Upload')

class AnnotationForm(FlaskForm):
    pass  # We don't need any fields, just the CSRF protection

def create_app():
    app = Flask(__name__)

    # Database configuration
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Initialize CSRF protection
    csrf = CSRFProtect(app)

    with app.app_context():
        # Import models here to avoid circular imports
        from models import User, Sentence, Annotation
        db.create_all()
        create_admin_user()

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    # Register routes
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('annotate'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('annotate'))
        form = LoginForm()
        if form.validate_on_submit():
            username = form.data['username']
            password = form.data['password']
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for('annotate'))
            else:
                flash('Invalid username or password')
        return render_template('login.html', form=form)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('annotate'))
        form = RegisterForm()
        if form.validate_on_submit():
            username = form.data['username']
            password = form.data['password']
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists')
            else:
                new_user = User(username=username, role='annotator')
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('annotate'))
        return render_template('register.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/annotate')
    @login_required
    def annotate():
        # Find the first uncompleted sentence
        sentence = Sentence.query.outerjoin(Annotation).filter(
            (Annotation.id == None) | (Annotation.is_completed == False)
        ).order_by(Sentence.id).first()

        if not sentence:
            flash('All sentences have been annotated.')
            return redirect(url_for('completed'))

        return redirect(url_for('annotate_sentence', sentence_id=sentence.id))

    @app.route('/annotate/<int:sentence_id>', methods=['GET', 'POST'])
    @login_required
    def annotate_sentence(sentence_id):
        sentence = Sentence.query.get_or_404(sentence_id)
        form = AnnotationForm()

        if form.validate_on_submit():
            # Handle form submission (marking as complete)
            annotation = Annotation.query.filter_by(
                sentence_id=sentence_id,
                annotator_id=current_user.id
            ).first()

            if not annotation:
                annotation = Annotation(
                    sentence_id=sentence_id,
                    annotator_id=current_user.id,
                    is_completed=True
                )
                db.session.add(annotation)
            else:
                annotation.is_completed = True

            db.session.commit()
            flash('Annotation marked as complete.')
            return redirect(url_for('annotate'))

        # Get next and previous sentence IDs
        next_sentence = Sentence.query.filter(Sentence.id > sentence_id).order_by(Sentence.id).first()
        prev_sentence = Sentence.query.filter(Sentence.id < sentence_id).order_by(Sentence.id.desc()).first()

        # Create a shuffled list of model names
        models = ['model1', 'model2', 'model3']
        random.seed(sentence_id)  # Use sentence_id as seed for consistent shuffling
        shuffled_models = random.sample(models, len(models))

        return render_template('annotate.html', 
                               form=form,
                               sentence=sentence, 
                               next_id=next_sentence.id if next_sentence else None,
                               prev_id=prev_sentence.id if prev_sentence else None,
                               shuffled_models=shuffled_models)

    @app.route('/save_annotation', methods=['POST'])
    @login_required
    def save_annotation():
        try:
            data = request.json
            sentence_id = data.get('sentence_id')
            model_name = data.get('model_name')
            
            annotation = Annotation.query.filter_by(
                sentence_id=sentence_id,
                annotator_id=current_user.id,
                model_name=model_name
            ).first()

            if not annotation:
                annotation = Annotation(
                    sentence_id=sentence_id,
                    annotator_id=current_user.id,
                    model_name=model_name,
                    error_spans=[],
                    missing_content=[],
                    overall_score=50,
                    is_completed=False
                )
                db.session.add(annotation)

            if 'error_span' in data:
                annotation.error_spans.append(data['error_span'])
            if 'remove_error_span' in data:
                annotation.error_spans = [
                    span for span in annotation.error_spans 
                    if not (span['start'] == data['remove_error_span']['start'] and span['end'] == data['remove_error_span']['end'])
                ]
            if 'missing_content' in data:
                annotation.missing_content.append(data['missing_content'])
            if 'remove_missing_content' in data:
                annotation.missing_content = [
                    mc for mc in annotation.missing_content 
                    if mc['type'] != data['remove_missing_content']['type']
                ]
            if 'overall_score' in data:
                annotation.overall_score = data['overall_score']

            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400



    @app.route('/completed')
    @login_required
    def completed():
        return render_template('completed.html')

    @app.route('/admin/upload', methods=['GET', 'POST'])
    @login_required
    def admin_upload():
        if current_user.role != 'admin':
            flash('You do not have permission to access this page.')
            return redirect(url_for('annotate'))

        form = CSVUploadForm()

        if form.validate_on_submit():
            file = form.file.data
            if file and file.filename.endswith('.csv'):
                filename = secure_filename(file.filename)
                file_content = file.read().decode('utf-8')
                csv_file = StringIO(file_content)
                csv_reader = csv.DictReader(csv_file)
                
                for row in csv_reader:
                    new_sentence = Sentence(
                        original_text=row['original_text'],
                        translation_method=row['translation_method'],
                        model1_name=row['model1_name'],
                        model1_translation=row['model1_translation'],
                        model2_name=row['model2_name'],
                        model2_translation=row['model2_translation'],
                        model3_name=row['model3_name'],
                        model3_translation=row['model3_translation']
                    )
                    db.session.add(new_sentence)
                
                db.session.commit()
                flash('CSV file successfully uploaded and processed.')
                return redirect(url_for('admin_dashboard'))
        
        return render_template('admin/upload.html', form=form)

    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        if current_user.role != 'admin':
            flash('You do not have permission to access this page.')
            return redirect(url_for('annotate'))
        return render_template('admin/dashboard.html')

    @app.route('/get_annotations/<int:sentence_id>')
    @login_required
    def get_annotations(sentence_id):
        annotations = Annotation.query.filter_by(
            sentence_id=sentence_id,
            annotator_id=current_user.id
        ).all()
        
        return jsonify({
            'annotations': [
                {
                    'model_name': ann.model_name,
                    'error_spans': ann.error_spans or [],
                    'missing_content': ann.missing_content or [],
                    'overall_score': ann.overall_score
                }
                for ann in annotations
            ]
        })

    return app

def create_admin_user():
    from models import User
    admin_username = os.environ.get('ADMIN_USERNAME')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    
    admin_user = User.query.filter_by(username=admin_username).first()
    if not admin_user:
        admin_user = User(username=admin_username, role='admin')
        admin_user.set_password(admin_password)
        db.session.add(admin_user)
        db.session.commit()
        print(f"Admin user '{admin_username}' created.")
    else:
        print(f"Admin user '{admin_username}' already exists.")

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)