import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Firebase
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID')
    FIREBASE_PRIVATE_KEY = os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n')
    FIREBASE_CLIENT_EMAIL = os.getenv('FIREBASE_CLIENT_EMAIL')
    
    # WhatsApp Automation
    MIN_DELAY_SECONDS = int(os.getenv('MIN_DELAY_SECONDS', '15'))
    MAX_DELAY_SECONDS = int(os.getenv('MAX_DELAY_SECONDS', '30'))
    DEFAULT_COUNTRY_CODE = os.getenv('DEFAULT_COUNTRY_CODE', '91')  # Default to India (91)
    
    # Server
    PORT = int(os.getenv('PORT', '5000'))
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Paths
    UPLOAD_FOLDER = 'uploads'
    SESSION_FOLDER = 'sessions/whatsapp'
    ALLOWED_EXTENSIONS = {'xlsx', 'csv'}
    
    @staticmethod
    def validate():
        """Validate that required configuration is present"""
        required = [
            'FIREBASE_PROJECT_ID',
            'FIREBASE_PRIVATE_KEY',
            'FIREBASE_CLIENT_EMAIL'
        ]
        missing = []
        for key in required:
            if not getattr(Config, key):
                missing.append(key)
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
