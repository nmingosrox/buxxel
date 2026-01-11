import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration shared across environments."""
    SECRET_KEY = os.environ.get("SECRET_KEY")

    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")  # Server-side admin access
    SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")        # Client-side browser access

    UPLOADCARE_PUBLIC_KEY = os.environ.get("UPLOADCARE_PUBLIC_KEY")
    UPLOADCARE_SECRET_KEY = os.environ.get("UPLOADCARE_SECRET_KEY")

    COMMISSION_RATE = 0.10


class DevelopmentConfig(Config):
    """Configuration for local development."""
    DEBUG = True
    TESTING = True


class ProductionConfig(Config):
    """Configuration for production deployment."""
    DEBUG = False
    TESTING = False
