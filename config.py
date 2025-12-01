import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    # The SECRET_KEY is crucial for session security and should be a long,
    # random string set in the environment. It should NOT have a default value.
    # Generate one with: python -c 'import secrets; print(secrets.token_hex(16))'
    SECRET_KEY = os.environ.get('SECRET_KEY')

    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") # For server-side admin access
    SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")       # For client-side browser access
    UPLOADCARE_PUBLIC_KEY = os.environ.get("UPLOADCARE_PUBLIC_KEY")
    UPLOADCARE_SECRET_KEY = os.environ.get("UPLOADCARE_SECRET_KEY")

    # You can add other config like COMMISSION_RATE here
    COMMISSION_RATE = 0.10