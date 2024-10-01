from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.ext.mutable import MutableList


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(1024))
    role = db.Column(db.String(20), nullable=False)
    last_annotated_set_id = db.Column(db.Integer, nullable=True, default=None)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Sentence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_text = db.Column(db.Text, nullable=False)
    translation_method = db.Column(db.String(50), nullable=False)
    model1_name = db.Column(db.String(100), nullable=False)
    model1_translation = db.Column(db.Text, nullable=False)
    model2_name = db.Column(db.String(100), nullable=False)
    model2_translation = db.Column(db.Text, nullable=False)
    model3_name = db.Column(db.String(100), nullable=False)
    model3_translation = db.Column(db.Text, nullable=False)
    model4_name = db.Column(db.String(100), nullable=False)
    model4_translation = db.Column(db.Text, nullable=False)

    def __getitem__(self, key):
        return getattr(self, key)

class Annotation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sentence_id = db.Column(db.Integer, db.ForeignKey('sentence.id'))
    annotator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    model_name = db.Column(db.String(64))

    error_spans = db.Column(
        MutableList.as_mutable(db.JSON), default=[]
    )
    missing_content = db.Column(
        MutableList.as_mutable(db.JSON), default=[]
    )

    overall_score = db.Column(db.Integer, default=50)
    is_completed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    annotator = db.relationship('User', backref=db.backref('annotations', lazy=True))
    sentence = db.relationship('Sentence', backref=db.backref('annotations', lazy=True))
