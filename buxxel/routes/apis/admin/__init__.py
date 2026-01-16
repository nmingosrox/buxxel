"""
Admin APIs
==========

Provides access to admin-specific API blueprints for listings, orders, and users.
"""

from .admin_listings_api import admin_listings_api_bp
from .admin_orders_api import admin_orders_api_bp
from .admin_profiles_api import admin_profiles_api_bp

__all__ = [
    "admin_listings_api_bp",
    "admin_orders_api_bp",
    "admin_profiles_api_bp",
]
