from flask import Blueprint, request, jsonify, current_app
from buxxel.extensions import supabase
from buxxel.auth.decorators import auth_required

profiles_api_bp = Blueprint('profiles_api', __name__, url_prefix='/api')

@profiles_api_bp.route('/me/profile', methods=['GET', 'PUT'])
@auth_required
def handle_my_profile(user):
    """Handles fetching or updating the authenticated user's profile."""
    if request.method == 'GET':
        try:
            profile = supabase.table('profiles').select("username").eq('id', user.id).single().execute()
            return jsonify(profile.data or {}), 200
        except Exception as e:
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    if request.method == 'PUT':
        data = request.get_json()
        username = data.get('username')
        if not username or len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters long."}), 400
        
        update_data = {"username": username, "updated_at": "now()"}
        try:
            response = supabase.table('profiles').update(update_data).eq('id', user.id).execute()
            return jsonify(response.data[0]), 200
        except Exception as e:
            return jsonify({"error": f"Failed to update profile: {str(e)}"}), 500

@profiles_api_bp.route('/profiles/<user_id>', methods=['GET'])
def get_public_profile(user_id):
    """Fetches public profile data for a given user ID."""
    try:
        profile_res = supabase.table('profiles').select("username").eq('id', user_id).single().execute()
        if not profile_res.data:
            return jsonify({"error": "Purveyor not found."}), 404

        username = profile_res.data.get('username') or f"Purveyor #{user_id[:8]}"
        
        # Call the secure RPC function to count active listings.
        listings_count_res = supabase.rpc('count_user_active_listings', {'profile_id': user_id}).execute()
        active_listings_count = listings_count_res.data
        
        profile_data = {"user_id": user_id, "username": username, "active_listings_count": active_listings_count}
        return jsonify(profile_data), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching public profile for {user_id}: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500