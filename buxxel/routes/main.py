from flask import Blueprint, render_template, request, redirect, url_for
from buxxel import db
from buxxel.models import User, Product, Service, Order
from flask_login import login_required, current_user

main_bp = Blueprint("main", __name__)

# --------------------
# Home / Landing Page
# --------------------
@main_bp.route("/")
def index():
    return render_template("index.html", current_user=current_user)

# --------------------
# Listings Page
# --------------------
@main_bp.route("/listings")
def listings():
    products = Product.query.all()
    services = Service.query.all()
    return render_template("listings.html", listings=[products, services])

# --------------------
# Shop Page
# --------------------
@main_bp.route("/shop")
def shop():
    return render_template("shop.html")

# --------------------
# Search Page
# --------------------
@main_bp.route("/search")
def search():
    query = request.args.get("q", "")
    results = []

    if query:
        # Example: search Listings or Products
        results = Listing.query.filter(Listing.title.ilike(f"%{query}%")).all()

    return render_template("search.html", query=query, results=results)

# --------------------
# Cart Page
# --------------------
@main_bp.route("/cart")
@login_required
def cart():
    # Fetch cart items for the logged-in user
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    return render_template("cart.html", cart_items=cart_items)

# --------------------
# Orders Page
# --------------------
@main_bp.route("/orders")
@login_required
def orders():
    # Fetch orders for the logged-in user
    user_orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template("orders.html", orders=user_orders)

# --------------------
# Contact Page
# --------------------
@main_bp.route("/contact")
def contact():
    return render_template("contact.html")

# --------------------
# Checkout Page
# --------------------
@main_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    if request.method == "POST":
        items = request.form.getlist("items")  # e.g. list of listing IDs
        quantities = request.form.getlist("quantities")

        # Create new order
        new_order = Order(user_id=current_user.id, status="pending")
        db.session.add(new_order)
        db.session.flush()

        # Add items to order
        for listing_id, qty in zip(items, quantities):
            order_item = OrderItem(
                order_id=new_order.id,
                listing_id=int(listing_id),
                quantity=int(qty)
            )
            db.session.add(order_item)

        db.session.commit()
        return redirect(url_for("main.order_confirmation", order_id=new_order.id))

    return render_template("checkout.html")

# --------------------
# Order Confirmation
# --------------------
@main_bp.route("/order/<int:order_id>/confirmation")
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("order_confirmation.html", order=order)
