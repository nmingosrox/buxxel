import os
from dotenv import load_dotenv

load_dotenv(".env")

class Config:
    """Base configuration."""
    # The SECRET_KEY is crucial for session security and should be a long,
    # random string set in the environment. It should NOT have a default value.
    # Generate one with: python -c 'import secrets; print(secrets.token_hex(16))'
    SECRET_KEY = os.environ.get("SECRET_KEY")

    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")  # For server-side admin access
    SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")        # For client-side browser access

    UPLOADCARE_PUBLIC_KEY = os.environ.get("UPLOADCARE_PUBLIC_KEY")
    UPLOADCARE_SECRET_KEY = os.environ.get("UPLOADCARE_SECRET_KEY")
    
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
