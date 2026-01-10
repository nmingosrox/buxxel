from flask import Blueprint, render_template, jsonify, request, current_app
from buxxel.auth.decorators import admin_required
from buxxel.extensions import supabase_admin
import requests
import re # For extracting UUID from Uploadcare URLs

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_required
def dashboard(user):
    """Renders the main admin dashboard page."""
    return render_template('admin/dashboard.html')

# We can add placeholder routes for other admin pages
@admin_bp.route('/users')
@admin_required
def manage_users(user):
    """Renders the page for managing all users."""
    return render_template('admin/users.html', page_title="Manage Users")

@admin_bp.route('/orders')
@admin_required
def manage_orders(user):
    """Renders the page for managing all orders."""
    return render_template('admin/orders.html')

@admin_bp.route('/listings')
@admin_required
def manage_listings(user):
    """Renders the page for managing all listings."""
    return render_template('admin/listings.html', page_title="Manage Listings")

# --- API Routes for Admin Panel ---

@admin_bp.route('/api/users')
@admin_required
def api_get_users(user):
    """API endpoint to get all users."""
    try:
        # Fetches users from the 'profiles' table which should contain roles
        response = supabase_admin.table('profiles').select('id, email, user_role, created_at').execute()
        if response.data:
            return jsonify(response.data)
        return jsonify([])
    except Exception as e:
        print(f"Error fetching users: {e}")
        return jsonify({"error": "Failed to fetch users"}), 500

@admin_bp.route('/api/listings')
@admin_required
def api_get_listings(user):
    """API endpoint to get all listings with purveyor info."""
    try:
        # Get pagination, sorting, and search parameters from the request query string
        page = request.args.get('page_num', 1, type=int)
        per_page = request.args.get('page_size', 20, type=int)
        search_query = request.args.get('search_query', '', type=str)
        sort_column = request.args.get('sort_column', 'created_at', type=str)
        sort_direction = request.args.get('sort_direction', 'desc', type=str)

        # Prepare parameters for the RPC call
        params = {
            'page_num': page,
            'page_size': per_page,
            'search_query': search_query,
            'sort_column': sort_column,
            'sort_direction': sort_direction
        }

        # Call the RPC function with the specified parameters
        response = supabase_admin.rpc('get_admin_listings', params).execute()

        if response.data:
            return jsonify(response.data)
        return jsonify([])
    except Exception as e:
        print(f"Error fetching listings: {e}")
        return jsonify({"error": "Failed to fetch listings"}), 500

@admin_bp.route('/api/listings/<int:listing_id>', methods=['DELETE'])
@admin_required
def api_delete_listing(user, listing_id):
    """API endpoint to delete a specific listing and its images from Uploadcare."""
    try:
        # 1. Fetch listing details to get image_urls before deleting the listing itself
        # We use a SECURITY DEFINER RPC to bypass RLS.
        response = supabase_admin.rpc('get_listing_images_admin', {'target_id': listing_id}).execute()
        
        if not response.data:
            return jsonify({"error": "Listing not found"}), 404
        
        # The RPC response is a list, so we need to get the first item.
        listing_data = response.data[0]
        image_urls = listing_data.get('image_urls', [])

        # 2. Delete the listing from Supabase by calling our secure RPC function
        # Supabase returns a response object; check for errors.
        delete_response = supabase_admin.rpc('delete_listing_admin', {'target_id': listing_id}).execute()

        # The RPC call doesn't return a count, so we can't check it.
        # We rely on the initial fetch to confirm the listing existed.
        # If the RPC fails, it will raise an exception caught below.

        # 3. Delete images from Uploadcare
        uploadcare_public_key = current_app.config.get('UPLOADCARE_PUBLIC_KEY')
        uploadcare_secret_key = current_app.config.get('UPLOADCARE_SECRET_KEY')

        if not uploadcare_public_key or not uploadcare_secret_key:
            print("Uploadcare API keys not configured. Skipping image deletion.")
        else:
            for url in image_urls:
                try:
                    # Extract UUID from Uploadcare CDN URL (e.g., https://ucarecdn.com/UUID/filename.jpg)
                    # UUID format: 8-4-4-4-12 hex characters
                    uuid_match = re.search(r'ucarecdn\.com/([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', url)
                    if uuid_match:
                        file_uuid = uuid_match.group(1)
                        uploadcare_delete_url = f"https://api.uploadcare.com/files/{file_uuid}/"
                        
                        headers = {
                            'Authorization': f'Uploadcare.Simple {uploadcare_public_key}:{uploadcare_secret_key}',
                            'Accept': 'application/vnd.uploadcare-v0.7+json'
                        }
                        
                        delete_file_response = requests.delete(uploadcare_delete_url, headers=headers)
                        delete_file_response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                        print(f"Successfully deleted Uploadcare file: {file_uuid}")
                    else:
                        print(f"Could not extract UUID from URL: {url}")
                except requests.exceptions.RequestException as uc_e:
                    print(f"Error deleting Uploadcare file {url}: {uc_e}")
                    # Log the error but continue to try deleting other files

        return jsonify({"message": "Listing and associated images deleted successfully"}), 200

    except Exception as e:
        print(f"Error deleting listing {listing_id}: {e}")
        return jsonify({"error": f"Failed to delete listing: {str(e)}"}), 500
