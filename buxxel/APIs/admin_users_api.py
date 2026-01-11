from flask import Blueprint, jsonify, current_app
from buxxel.decorators import admin_api_required
from buxxel.database import supabase_admin

admin_users_api_bp = Blueprint("admin_users_api", __name__, url_prefix="/api/admin/users")

@admin_users_api_bp.route("/", methods=["GET"])
@admin_api_required
def get_users(user):
    """Fetch all users via RPC."""
    try:
        response = supabase_admin.rpc("get_all_users", {}).execute()
        return jsonify(response.data or [])
    except Exception as e:
        current_app.logger.error(f"Error fetching users: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch users"}), 500
