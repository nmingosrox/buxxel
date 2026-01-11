from flask import Blueprint, render_template
from buxxel.decorators import page_auth_required   # corrected import name

dashboard_bp = Blueprint("dashboard", __name__)   # fixed blueprint definition

@dashboard_bp.route("/dashboard")
@page_auth_required
def dashboard(user):
    """Renders the user dashboard page (requires login)."""
    return render_template("dashboard.html", user=user)

@dashboard_bp.route("/my-orders")
@page_auth_required
def my_orders_page(user):
    """Renders the user's orders page (requires login)."""
    return render_template("my_orders.html", user=user)   # fixed function name and render_template spelling
