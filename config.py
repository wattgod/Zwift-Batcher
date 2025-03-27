import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///workouts.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AWS S3
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME', 'gravel-god-workouts')
    AWS_REGION = os.getenv('AWS_REGION', 'us-west-2')
    
    # File Storage
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', os.path.expanduser('~/Desktop'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Colors
    GG_COLORS = {
        'brown_dark': '#59473C',
        'brown_medium': '#8C7568',
        'brown_light': '#A68E80',
        'beige': '#BFA595',
        'turquoise': '#40E0D0'
    } 