from flask import Blueprint, request, jsonify, current_app
from buxxel.database import supabase
from postgrest import APIError
from buxxel.decorators import auth_required

listings_api_bp = Blueprint('listings_api', __name__, url_prefix='/api')

@listings_api_bp.route('/listings/paged', methods=['GET'])
def get_paged_listings():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', None, type=str)
    search_term = request.args.get('search', None, type=str)
    per_page = 12

    try:
        params = {
            'page_num': page,
            'page_size': per_page,
            'search_query': search_term if search_term else None,
            'category_filter': category if category else None
        }
        
        response = supabase.rpc('get_public_listings_paged', params).execute()

        if response.data:
            # response.data is already a list of listing objects
            listings = response.data
            # Use total_count if provided, otherwise fallback to length
            total_listings = response.data[0].get('total_count', len(response.data))
            has_next = (page * per_page) < total_listings
        else:
            listings = []
            has_next = False

        return jsonify({
            "listings": listings,
            "pagination": {
                "page": page,
                "has_next": has_next
            }
        }), 200
    except APIError as e:
        current_app.logger.error(f"Supabase API Error fetching paged listings: {e.json()}")
        return jsonify({"error": "Failed to load listings due to a database error."}), 500
    except Exception as e:
        current_app.logger.error(f"Error fetching paged listings: {e}")
        return jsonify({"error": "An unexpected error occurred while loading listings."}), 500

@listings_api_bp.route('/listings', methods=['POST'])
@auth_required
def create_listing(user):
    try:
        data = request.form
        # --- Improved Validation ---
        if not data.get('name') or not data.get('description') or not data.get('tags'):
            return jsonify({"error": "Name, description, and tags are required."}), 400
        if not data.get('image_url'):
            return jsonify({"error": "A product image is required."}), 400
        if not data.get('price') or not data.get('stock') or float(data.get('price', 0)) < 0 or int(data.get('stock', 0)) < 0:
            return jsonify({"error": "Price and stock must be provided and be valid numbers."}), 400

        price = float(data.get('price'))
        stock = int(data.get('stock'))
        final_price = price * (1 + current_app.config['COMMISSION_RATE'])
        tags = [tag.strip().lower() for tag in data.get('tags', '').split(',') if tag.strip()]

        listing_data = {
            "name": data.get('name'), "price": final_price, "image_urls": [data.get('image_url')],
            "tags": tags, "category": tags[0] if tags else 'general', "description": data.get('description'),
            "stock": stock, "pre_zero_stock": stock if stock > 0 else 1, "user_id": user.id
        }

        # This is the definitive, thread-safe way to perform an action as a user.
        # We use the main `supabase` client (with service_role) to perform an RPC call
        # that runs with the permissions of the user who is making the request.
        jwt = request.headers.get('Authorization').split(' ')[1]
        response = supabase.rpc('create_listing_as_user', {'listing_data': listing_data, 'user_jwt': jwt}).execute()

        return jsonify(response.data), 201
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Price and stock must be valid numbers.{e}"}), 400
    except APIError as e:
        current_app.logger.error(f"Listing creation error: {e.json()}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred during listing creation."}), 500

@listings_api_bp.route('/me/listings', methods=['GET'])
@auth_required
def get_user_listings(user):
    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort_by', 'created_at', type=str)
    sort_order = request.args.get('sort_order', 'desc', type=str)
    per_page = 5

    try:
        allowed_sort_columns = ['created_at', 'name', 'price', 'stock']
        if sort_by not in allowed_sort_columns: sort_by = 'created_at'
        
        jwt = request.headers.get('Authorization').split(' ')[1]
        
        params = {
            'user_jwt': jwt,
            'page_num': page,
            'page_size': per_page,
            'search_query': search_term if search_term else None,
            'sort_column': sort_by,
            'sort_direction': sort_order.lower()
        }
        
        response = supabase.rpc('get_listings_for_authenticated_user', params).execute()

        if response.data:
            listings = [item['listing'] for item in response.data]
            total_listings = response.data[0]['total_count']
            has_next = (page * per_page) < total_listings
        else:
            listings = []
            total_listings = 0
            has_next = False

        return jsonify({"listings": listings, "pagination": {"page": page, "has_next": has_next, "total_listings": total_listings}}), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching user listings for {user.id}: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@listings_api_bp.route('/listings/<listing_id>', methods=['GET', 'PUT', 'DELETE'])
@auth_required
def handle_listing(user, listing_id):
    try:
        if request.method == 'GET':
            response = supabase.table('listings').select("*").eq('id', listing_id).eq('user_id', user.id).single().execute()
            if not response.data: return jsonify({"error": "Listing not found or you do not have permission."}), 404
            return jsonify(response.data), 200

        if request.method == 'PUT':
            data = request.form
            if not all([data.get('name'), data.get('price'), data.get('description'), data.get('stock'), data.get('image_url')]):
                return jsonify({"error": "Missing required listing data."}), 400
            
            price = float(data.get('price'))
            stock = int(data.get('stock'))
            final_price = price * (1 + current_app.config['COMMISSION_RATE'])
            tags = [tag.strip().lower() for tag in data.get('tags', '').split(',') if tag.strip()]

            update_data = {
                "name": data.get('name'), "price": final_price, "description": data.get('description'),
                "stock": stock, "category": tags[0] if tags else 'general', "image_urls": [data.get('image_url')], "tags": tags
            }
            response = supabase.table('listings').update(update_data).eq('id', listing_id).eq('user_id', user.id).execute()
            if not response.data: return jsonify({"error": "Update failed. Listing not found or permission denied."}), 404
            return jsonify(response.data[0]), 200

        if request.method == 'DELETE':
            response = supabase.table('listings').delete().eq('id', listing_id).eq('user_id', user.id).execute()
            if not response.data: return jsonify({"error": "Delete failed. Listing not found or permission denied."}), 404
            return jsonify({"message": "Listing deleted successfully."}), 200

    except (ValueError, TypeError) as e:
        current_app.logger.warning(f"Invalid data for listing {listing_id}: {e}")
        return jsonify({"error": "Price and stock must be valid numbers."}), 400
    except Exception as e:
        current_app.logger.error(f"Error handling listing {listing_id} for user {user.id}: {e}", exc_info=True)
        return jsonify({"error": "An unexpected server error occurred."}), 500

@listings_api_bp.route('/listings/<listing_id>/status', methods=['PUT'])
@auth_required
def handle_listing_status(user, listing_id):
    data = request.get_json()
    new_status = data.get('status')
    if new_status not in ['in_stock', 'out_of_stock']:
        return jsonify({"error": "Invalid status provided."}), 400

    try:
        listing_response = supabase.table('listings').select("stock, pre_zero_stock").eq('id', listing_id).eq('user_id', user.id).single().execute()
        if not listing_response.data: return jsonify({"error": "Listing not found or you do not have permission."}), 404

        current_listing = listing_response.data
        update_data = {}
        if new_status == 'out_of_stock':
            if current_listing['stock'] > 0: update_data['pre_zero_stock'] = current_listing['stock']
            update_data['stock'] = 0
        elif new_status == 'in_stock':
            update_data['stock'] = current_listing.get('pre_zero_stock', 1) or 1

        response = supabase.table('listings').update(update_data).eq('id', listing_id).execute()
        if not response.data: return jsonify({"error": "Failed to update listing status."}), 500
        return jsonify(response.data[0]), 200
    except Exception as e:
        current_app.logger.error(f"Error updating status for listing {listing_id}: {e}", exc_info=True)
        return jsonify({"error": "An unexpected server error occurred."}), 500


@listings_api_bp.route('/categories/popular', methods=['GET'])
def get_categories():
    try:
        # Call Supabase RPC
        response = supabase.rpc('get_categories', {'limit_count': 10}).execute()

        # 1. Handle explicit Supabase errors first
        if response.error:
            current_app.logger.error(
                f"Supabase RPC error: {response.error}",
                exc_info=True
            )
            return jsonify({
                "error": "Failed to load categories",
                "details": str(response.error)
            }), 502

        # 2. Handle empty data
        if not response.data:
            current_app.logger.warning("No categories returned from Supabase")
            return jsonify({
                "error": "No categories found"
            }), 404

        # 3. Success case
        return jsonify(response.data), 200

    except Exception as e:
        # Catch unexpected Flask or runtime errors
        current_app.logger.error(
            f"Unexpected error fetching categories: {e}",
            exc_info=True
        )
        return jsonify({"error": "Internal server error while loading categories."}), 500
