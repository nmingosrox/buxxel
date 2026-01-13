from flask import Blueprint, request, jsonify, current_app
from buxxel.extensions import supabase, supabase_admin
from buxxel.auth.decorators import auth_required

orders_api_bp = Blueprint('orders_api', __name__, url_prefix='/api')

@orders_api_bp.route('/orders', methods=['POST'])
@auth_required
def create_order(user):
    """
    Creates a new order for the authenticated user.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request body."}), 400

    # Extract data from the payload sent by the frontend
    shipping_address = data.get('shipping_address')
    order_details = data.get('order_details')
    total_price = data.get('total_price')

    if not all([shipping_address, order_details, total_price]):
        return jsonify({"error": "Missing required order information."}), 400

    try:
        # Prepare parameters for the RPC call
        # We can securely pass the user.id because the @auth_required decorator has validated it.
        params = {
            "user_id_in": user.id,
            "total_price_in": total_price,
            "shipping_address_in": shipping_address,
            "order_details_in": order_details
        }

        # Call the RPC function using the ADMIN client.
        # The endpoint is already protected by @auth_required, so we know the user is valid.
        # Using the admin client guarantees we have permission to EXECUTE the SECURITY DEFINER function.
        response = supabase_admin.rpc('create_order_for_user', params).execute()
        return jsonify(response.data[0]), 201
    except Exception as e:
        current_app.logger.error(f"Error creating order for user {user.id}: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while placing your order."}), 500

@orders_api_bp.route('/me/orders', methods=['GET'])
@auth_required
def get_my_orders(user):
    """
    Fetches all orders for the currently authenticated user.
    """
    try:
        # Call the secure SECURITY DEFINER RPC, passing the validated user's ID.
        # We use the standard `supabase` client here, as the function itself has elevated privileges.
        params = {"user_id_in": user.id}
        response = supabase.rpc('get_orders_for_user', params).execute()
        return jsonify(response.data), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching orders for user {user.id}: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while fetching your orders."}), 500