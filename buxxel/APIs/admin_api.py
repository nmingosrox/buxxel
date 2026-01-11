from flask import Blueprint, jsonify, request, current_app
from buxxel.decorators import admin_required
from buxxel.database import supabase_admin
import requests
import re

admin_api_bp = Blueprint("admin_api", __name__, url_prefix="/admin/api")

@admin_api_bp.route("/users")
@admin_required
def api_get_users(user):
    """API endpoint to get all users via RPC."""
    try:
        response = supabase_admin.rpc("get_all_users", {}).execute()
        return jsonify(response.data or [])
    except Exception as e:
        current_app.logger.error(f"Error fetching users via RPC: {e}")
        return jsonify({"error": "Failed to fetch users"}), 500

@admin_api_bp.route("/listings")
@admin_required
def api_get_listings(user):
    """API endpoint to get all listings with purveyor info."""
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
        current_app.logger.error(f"Error fetching listings: {e}")
        return jsonify({"error": "Failed to fetch listings"}), 500

@admin_api_bp.route("/listings/<int:listing_id>", methods=["DELETE"])
@admin_required
def api_delete_listing(user, listing_id):
    """API endpoint to delete a specific listing and its images from Uploadcare."""
    try:
        response = supabase_admin.rpc("get_listing_images_admin", {"target_id": listing_id}).execute()
        if not response.data:
            return jsonify({"error": "Listing not found"}), 404

        listing_data = response.data[0]
        image_urls = listing_data.get("image_urls", [])

        supabase_admin.rpc("delete_listing_admin", {"target_id": listing_id}).execute()

        uploadcare_public_key = current_app.config.get("UPLOADCARE_PUBLIC_KEY")
        uploadcare_secret_key = current_app.config.get("UPLOADCARE_SECRET_KEY")

        if uploadcare_public_key and uploadcare_secret_key:
            for url in image_urls:
                try:
                    uuid_match = re.search(
                        r"ucarecdn\.com/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})",
                        url,
                    )
                    if uuid_match:
                        file_uuid = uuid_match.group(1)
                        uploadcare_delete_url = f"https://api.uploadcare.com/files/{file_uuid}/"
                        headers = {
                            "Authorization": f"Uploadcare.Simple {uploadcare_public_key}:{uploadcare_secret_key}",
                            "Accept": "application/vnd.uploadcare-v0.7+json",
                        }
                        delete_file_response = requests.delete(uploadcare_delete_url, headers=headers)
                        delete_file_response.raise_for_status()
                        current_app.logger.info(f"Deleted Uploadcare file: {file_uuid}")
                except requests.exceptions.RequestException as uc_e:
                    current_app.logger.error(f"Error deleting Uploadcare file {url}: {uc_e}")

        return jsonify({"message": "Listing and associated images deleted successfully"}), 200

    except Exception as e:
        current_app.logger.error(f"Error deleting listing {listing_id}: {e}")
        return jsonify({"error": f"Failed to delete listing: {str(e)}"}), 500
