# Translation Error Span Annotation Tool

This is a Flask-based web application for annotating error spans in translations. It allows users to highlight errors, mark missing content, and provide overall scores for translations.

## Local Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/translation-annotation-tool.git
   cd translation-annotation-tool
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with the following content:
   ```
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=secure_admin_password
   SECRET_KEY=your_secret_key_here
   FLASK_APP=app.py
   ```

5. Initialize the database:
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. Run the application:
   ```
   flask run
   ```

7. Access the application at `http://localhost:5000`

## Heroku Deployment

1. Make sure you have the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed and you're logged in.

2. Create a new Heroku app:
   ```
   heroku create your-app-name
   ```

3. Add a PostgreSQL database to your Heroku app:
   ```
   heroku addons:create heroku-postgresql:hobby-dev
   ```

4. Set the necessary environment variables:
   ```
   heroku config:set ADMIN_USERNAME=admin
   heroku config:set ADMIN_PASSWORD=secure_admin_password
   heroku config:set SECRET_KEY=your_secret_key_here
   ```

5. Add a `Procfile` to the root directory with the following content:
   ```
   web: gunicorn app:app
   ```

6. Add `gunicorn` to your `requirements.txt` file:
   ```
   echo "gunicorn" >> requirements.txt
   ```

7. Commit your changes:
   ```
   git add .
   git commit -m "Prepare for Heroku deployment"
   ```

8. Push your code to Heroku:
   ```
   git push heroku main
   ```

9. Run database migrations on Heroku:
   ```
   heroku run flask db upgrade
   ```

10. Open your application:
    ```
    heroku open
    ```

## Usage

1. Register a new account or log in with existing credentials.
2. As an admin, upload CSV files containing sentences to be annotated.
3. Regular users can access the annotation interface to highlight errors, mark missing content, and provide overall scores for translations.
4. Admins can view and manage tasks through the admin dashboard.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)