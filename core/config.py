"""
Configuration Management for Ardelis Technologies
"""
import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'config', '.env.production'))

class Config:
    """Production configuration for Ardelis Technologies"""

    # API Configuration
    ZAI_API_KEY = os.getenv('ZAI_API_KEY')

    # LinkedIn Configuration
    LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
    LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
    LINKEDIN_REDIRECT_URI = os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost:8000')

    # Business Configuration
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'outputs')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Scheduler Configuration
    SCHEDULER_CHECK_INTERVAL = int(os.getenv('SCHEDULER_CHECK_INTERVAL', '60'))
    RATE_LIMIT_DELAY = int(os.getenv('RATE_LIMIT_DELAY', '6'))

    # Web Server Configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '5000'))
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

    # Ensure directories exist
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories"""
        directories = [
            cls.OUTPUT_DIR,
            'logs',
            'config',
            'data',
            'cache'
        ]

        for directory in directories:
            Path(directory).mkdir(exist_ok=True)

    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []

        if not cls.ZAI_API_KEY:
            errors.append("❌ ZAI_API_KEY is required in config/.env.production")

        if not cls.SECRET_KEY or cls.SECRET_KEY == 'your-secret-key-change-in-production':
            errors.append("❌ SECRET_KEY must be set to a secure value")

        if errors:
            print("\n⚠️ Configuration Errors:")
            for error in errors:
                print(f"  {error}")
            print("\n💡 Fix these in config/.env.production")
            return False

        return True

# Legacy compatibility (keep existing variables)
TOPICS_FILE = "topics.json"
LINKEDIN_OUTPUT_FILE = "content_calendar.json"
TWITTER_OUTPUT_FILE = "twitter_calendar.json"

# Load configuration
settings = Config()