from flask import Blueprint, render_template
from buxxel.auth.decorators import page_auth_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@dashboard_bp.route('/my-orders')
@page_auth_required
def my_orders_page(user):
    return render_template('my_orders.html')
