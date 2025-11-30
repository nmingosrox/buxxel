from flask import Blueprint, render_template
from buxxel.auth.decorators import admin_required

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
    return render_template('admin/dashboard.html', page_title="Manage Users") # Placeholder for user management

@admin_bp.route('/orders')
@admin_required
def manage_orders(user):
    """Renders the page for managing all orders."""
    return render_template('admin/orders.html')