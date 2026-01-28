import os
from dotenv import load_dotenv

# Load .env file from the same directory
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

class Config:
    """Base configuration."""
    # The SECRET_KEY is crucial for session security and should be a long,
    # random string set in the environment. It should NOT have a default value.
    # Generate one with: python -c 'import secrets; print(secrets.token_hex(16))'
    SECRET_KEY = os.environ.get("SECRET_KEY")

    SB_URL = os.environ.get("SB_URL")
    SB_PUBLISHABLE_KEY = os.environ.get("SB_PUBLISHABLE_KEY")  # For server side client browser access
    SB_SECRET_KEY = os.environ.get("SB_SECRET_KEY") # For server side admin access

    UC_PUBLIC_KEY = os.environ.get("UC_PUBLIC_KEY")
    UC_SECRET_KEY = os.environ.get("UC_SECRET_KEY")
    
    # CUSTOM ENVIRONMENT VARIABLES
    COMMISSION_RATE = 0.10

    # Environment toggle (development, production, etc.)
    # Tries to get flask environment to us in configuration
    # initialization and sets it to "development" if none 
    # is found
    FLASK_ENV = os.getenv("FLASK_ENV", "development")

class DevelopmentConfig(Config):
    """Configuration for local development."""
    DEBUG = True
    TESTING = True


class ProductionConfig(Config):
    """Configuration for production deployment."""
    DEBUG = False
    TESTING = False
