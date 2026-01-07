from flask import Blueprint, render_template
from flask_login import login_required, current_user

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# --------------------
# Admin Dashboard
# --------------------
@admin_bp.route("/")
@login_required
def dashboard():
    if not current_user.is_admin:
        return "Unauthorized", 403
    return render_template("admin/index.html")


# --------------------
# Manage Listings
# --------------------
@admin_bp.route("/listings")
@login_required
def admin_listings():
    if not current_user.is_admin:
        return "Unauthorized", 403
    return render_template("admin/listings.html")


# --------------------
# Manage Orders
# --------------------
@admin_bp.route("/orders")
@login_required
def admin_orders():
    if not current_user.is_admin:
        return "Unauthorized", 403
    return render_template("admin/orders.html")
