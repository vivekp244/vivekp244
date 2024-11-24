import os

class Config:
    # General Configuration
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'  # Enable debug based on environment variable
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_default_secret_key')  # Application secret key

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///blog.db')  # Database URI with default SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable SQLAlchemy event notifications (performance boost)

    # Flask-Security Configuration
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'your_default_password_salt')  # Password salt
    SECURITY_PASSWORD_HASH = 'bcrypt'  # Secure password hashing method

    # Flask-WTF Configuration
    WTF_CSRF_ENABLED = True  # Enable CSRF protection for forms
