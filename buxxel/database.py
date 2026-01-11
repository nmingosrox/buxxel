from supabase import create_client, Client

supabase: Client = None        # Standard client for user-specific operations
supabase_admin: Client = None  # Privileged client for admin tasks
