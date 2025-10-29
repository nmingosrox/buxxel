from flask import Blueprint, request, jsonify, current_app
from buxxel.extensions import supabase
from buxxel.auth.decorators import auth_required

listings_api_bp = Blueprint('listings_api', __name__, url_prefix='/api')

@listings_api_bp.route('/listings/paged', methods=['GET'])
def get_paged_listings():
    page = request.args.get('page', 1, type=int)
    tag = request.args.get('tag', None, type=str)
    search_term = request.args.get('search', None, type=str)
    per_page = 12
    start_index = (page - 1) * per_page
    end_index = start_index + per_page - 1

    try:
        query = supabase.table('listings').select("*", count='exact')
        if tag and tag != 'all':
            query = query.contains('tags', [tag])
        if search_term:
            query = query.ilike('name', f'%{search_term}%')

        response = query.order('id').range(start_index, end_index).execute()
        has_next = end_index < response.count - 1
        return jsonify({"listings": response.data, "pagination": {"page": page, "has_next": has_next}}), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching paged listings: {e}")
        return jsonify({"error": "Failed to load listings."}), 500

@listings_api_bp.route('/listings', methods=['POST'])
@auth_required
def create_listing(user):
    try:
        data = request.form
        if not all([data.get('name'), data.get('price'), data.get('description'), data.get('stock'), data.get('image_url')]):
            return jsonify({"error": "Missing required listing data."}), 400
        
        price = float(data.get('price'))
        stock = int(data.get('stock'))
        final_price = price * (1 + current_app.config['COMMISSION_RATE'])
        tags = [tag.strip().lower() for tag in data.get('tags', '').split(',') if tag.strip()]

        listing_data = {
            "name": data.get('name'), "price": final_price, "image_urls": [data.get('image_url')],
            "tags": tags, "category": tags[0] if tags else 'general', "description": data.get('description'),
            "stock": stock, "pre_zero_stock": stock if stock > 0 else 1, "user_id": user.id
        }
        response = supabase.table('listings').insert(listing_data).execute()
        return jsonify(response.data[0]), 201
    except (ValueError, TypeError):
        return jsonify({"error": "Price and stock must be valid numbers."}), 400
    except Exception as e:
        current_app.logger.error(f"Listing creation error: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred during listing creation."}), 500

@listings_api_bp.route('/me/listings', methods=['GET'])
@auth_required
def get_user_listings(user):
    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort_by', 'created_at', type=str)
    sort_order = request.args.get('sort_order', 'desc', type=str)
    per_page = 5
    start_index = (page - 1) * per_page
    end_index = start_index + per_page - 1

    try:
        allowed_sort_columns = ['created_at', 'name', 'price', 'stock']
        if sort_by not in allowed_sort_columns: sort_by = 'created_at'
        
        query = supabase.table('listings').select("*", count='exact').eq('user_id', user.id)
        if search_term:
            query = query.ilike('name', f'%{search_term}%')

        response = query.order(sort_by, desc=sort_order.lower() == 'desc').range(start_index, end_index).execute()
        has_next = end_index < response.count - 1
        return jsonify({"listings": response.data, "pagination": {"page": page, "has_next": has_next, "total_listings": response.count}}), 200
    except Exception as e:
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

@listings_api_bp.route('/tags/popular', methods=['GET'])
def get_popular_tags():
    try:
        response = supabase.rpc('get_popular_tags', {'limit_count': 10}).execute()
        if response.data: return jsonify(response.data), 200
        
        default_tags = [{'tag': 'electronics', 'count': 0}, {'tag': 'books', 'count': 0}]
        return jsonify(default_tags), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching popular tags: {e}")
        return jsonify({"error": "Could not load tags."}), 500