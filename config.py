import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///olympus.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Gemini AI
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Agora.io Streaming
    AGORA_APP_ID = os.getenv('AGORA_APP_ID', '')
    AGORA_APP_CERTIFICATE = os.getenv('AGORA_APP_CERTIFICATE', '')
    
    # App Settings
    ITEMS_PER_PAGE = 20
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
