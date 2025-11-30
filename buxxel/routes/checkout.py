from flask import Blueprint, render_template, flash
from buxxel.auth.decorators import page_auth_required

checkout_bp = Blueprint('checkout', __name__)

@checkout_bp.route('/checkout')
@page_auth_required
def checkout_page(user):
    """Renders the checkout page for a logged-in user."""
    # The cart data is stored in the browser's localStorage,
    # so the frontend will be responsible for fetching and displaying it.
    return render_template('checkout.html')

@checkout_bp.route('/order-success')
def order_success():
    return render_template('order_success.html')