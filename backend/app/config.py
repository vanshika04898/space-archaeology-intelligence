import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max upload
    ALLOWED_EXTENSIONS = {'csv', 'geojson', 'json'}
    MODELS_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'models')
    
    # Create directories if they don't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(MODELS_FOLDER, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dev.db')
    )

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://user:password@localhost/space_archaeology'
    )

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
