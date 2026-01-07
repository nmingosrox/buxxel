from flask import Blueprint, request, jsonify
from buxxel import db
from buxxel.models import Order, OrderItem, Listing, User

orders_bp = Blueprint("orders_api", __name__, url_prefix="/api/orders")

# --------------------
# GET all orders
# --------------------
@orders_bp.route("/", methods=["GET"])
def get_orders():
    orders = Order.query.all()
    return jsonify([{
        "id": o.id,
        "user_id": o.user_id,
        "status": o.status,
        "created_at": o.created_at.isoformat(),
        "items": [{
            "id": i.id,
            "listing_id": i.listing_id,
            "quantity": i.quantity
        } for i in o.items]
    } for o in orders])


# --------------------
# GET single order
# --------------------
@orders_bp.route("/<int:order_id>", methods=["GET"])
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify({
        "id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "created_at": order.created_at.isoformat(),
        "items": [{
            "id": i.id,
            "listing_id": i.listing_id,
            "quantity": i.quantity
        } for i in order.items]
    })


# --------------------
# CREATE new order
# --------------------
@orders_bp.route("/", methods=["POST"])
def create_order():
    data = request.get_json()
    user_id = data.get("user_id")
    items_data = data.get("items", [])

    # Create order
    new_order = Order(user_id=user_id, status="pending")
    db.session.add(new_order)
    db.session.flush()  # ensures new_order.id is available

    # Add items
    for item in items_data:
        listing = Listing.query.get(item["listing_id"])
        if not listing:
            return jsonify({"error": f"Listing {item['listing_id']} not found"}), 404

        order_item = OrderItem(
            order_id=new_order.id,
            listing_id=listing.id,
            quantity=item.get("quantity", 1)
        )
        db.session.add(order_item)

    db.session.commit()
    return jsonify({"message": "Order created", "id": new_order.id}), 201


# --------------------
# UPDATE order status
# --------------------
@orders_bp.route("/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.get_json()

    order.status = data.get("status", order.status)
    db.session.commit()
    return jsonify({"message": "Order updated"})


# --------------------
# DELETE order
# --------------------
@orders_bp.route("/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Order deleted"})
