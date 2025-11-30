from flask import Blueprint, jsonify, request, current_app
from buxxel.auth.decorators import admin_api_required
from buxxel.extensions import supabase_admin, create_client

admin_orders_api_bp = Blueprint('admin_orders_api', __name__, url_prefix='/api/admin')

@admin_orders_api_bp.route('/orders', methods=['GET'])
@admin_api_required
def get_all_orders(user):
    """
    Fetches all orders from the database.
    Protected by the admin_required decorator.
    """
    try:
        # Call the SECURITY DEFINER RPC function. This is the most reliable way to
        # bypass RLS for a privileged operation, as the function itself runs as admin.
        # We use the global supabase_admin client here, as calling an RPC is less
        # susceptible to the session tainting issue than a direct table query.
        response = supabase_admin.rpc('get_all_orders_for_admin', {}).execute()
        # Because the RPC returns SETOF json, the response.data is already the list of order objects.
        orders = response.data
        return jsonify(orders), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching all orders for admin: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while fetching orders."}), 500

@admin_orders_api_bp.route('/orders/<order_id>/status', methods=['PUT'])
@admin_api_required
def update_order_status(user, order_id):
    """
    Updates the status of a specific order.
    """
    data = request.get_json()
    new_status = data.get('status')

    if not new_status:
        return jsonify({"error": "Status is required."}), 400

    try:
        # Call the SECURITY DEFINER RPC to update the status.
        # This is the most reliable way to bypass RLS for this operation.
        params = {
            'order_id_in': order_id,
            'new_status_in': new_status
        }
        response = supabase_admin.rpc('update_order_status_as_admin', params).execute()

        if not response.data:
            return jsonify({"error": "Order not found or update failed."}), 404
        return jsonify(response.data[0]), 200
    except Exception as e:
        current_app.logger.error(f"Error updating status for order {order_id}: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred."}), 500