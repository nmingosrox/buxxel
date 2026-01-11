from supabase import create_client, Client
from buxxel.config import Config

# Standard client for user-specific operations (anon key)
supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)

# Privileged client for admin tasks (service key)
supabase_admin: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY)

# Utility function to create isolated clients (used in decorators for validation)
def create_supabase_client(url: str, key: str) -> Client:
    return create_client(url, key)
