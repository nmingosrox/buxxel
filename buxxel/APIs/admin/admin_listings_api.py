from flask import Blueprint, jsonify, request, current_app
from buxxel.decorators import admin_required
from buxxel.database import supabase_admin

admin_listings_api_bp = Blueprint("admin_listings_api", __name__, url_prefix="/api/admin/listings")

@admin_listings_api_bp.route("/", methods=["GET"])
@admin_required
def get_listings(user):
    """Fetch listings with purveyor info via RPC."""
    try:
        page = request.args.get("page_num", 1, type=int)
        per_page = request.args.get("page_size", 20, type=int)
        search_query = request.args.get("search_query", "", type=str)
        sort_column = request.args.get("sort_column", "created_at", type=str)
        sort_direction = request.args.get("sort_direction", "desc", type=str)

        params = {
            "page_num": page,
            "page_size": per_page,
            "search_query": search_query,
            "sort_column": sort_column,
            "sort_direction": sort_direction,
        }

        response = supabase_admin.rpc("get_admin_listings", params).execute()
        return jsonify(response.data or [])
    except Exception as e:
        current_app.logger.error(f"Error fetching listings: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch listings"}), 500
