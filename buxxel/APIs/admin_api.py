from flask import Blueprint, render_template
from buxxel.decorators import admin_required   # unified decorator import

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/")
@admin_required
def dashboard(user):
    """Renders the main admin dashboard page."""
    return render_template("admin/dashboard.html")

@admin_bp.route("/users")
@admin_required
def manage_users(user):
    """Renders the page for managing all users."""
    return render_template("admin/users.html", page_title="Manage Users")

@admin_bp.route("/orders")
@admin_required
def manage_orders(user):
    """Renders the page for managing all orders."""
    return render_template("admin/orders.html")

@admin_bp.route("/listings")
@admin_required
def manage_listings(user):
    """Renders the page for managing all listings."""
    return render_template("admin/listings.html", page_title="Manage Listings")
