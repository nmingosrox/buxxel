# categories_api.py
from flask import Blueprint, jsonify, current_app
from supabase import create_client, Client

# Initialize Blueprint
categories_api_bp = Blueprint('categories_api', __name__, url_prefix='/api/categories')

@categories_api_bp.route('/popular', methods=['GET'])
def get_popular_categories():
    """
    Fetch popular categories from Supabase using RPC function.
    Returns JSON response or error message.
    """
    try:
        # Call Supabase RPC function
        response = supabase.rpc('get_popular_categories', {'limit_count': 15}).execute()

        # Handle explicit Supabase errors
        if response.error:
            current_app.logger.error(
                f"Supabase RPC error: {response.error}",
                exc_info=True
            )
            return jsonify({
                "error": "Failed to load popular categories",
                "details": str(response.error)
            }), 502

        # Handle empty data
        if not response.data:
            current_app.logger.warning("No categories returned from Supabase")
            return jsonify({
                "error": "No categories found"
            }), 404

        # Success case
        return jsonify(response.data), 200

    except Exception as e:
        # Catch unexpected Flask/runtime errors
        current_app.logger.error(
            f"Unexpected error fetching popular categories: {e}",
            exc_info=True
        )
        return jsonify({"error": "Internal server error while loading popular categories."}), 500
