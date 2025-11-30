from supabase import create_client, Client

# Initialize the client as None. It will be configured in the app factory.
supabase: Client = None        # Standard client for user-specific operations
supabase_admin: Client = None  # Privileged client for admin tasks