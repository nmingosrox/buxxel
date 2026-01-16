# APIs/__init__.py
"""
APIs package
============

Provides access to core API modules and admin-specific APIs.
"""

# Core APIs
from .listings_api import listings_api_bp
from .orders_api import orders_api_bp
from .profiles_api import profiles_api_bp

# Admin APIs
from .admin.admin_listings_api import admin_listings_api_bp
from .admin.admin_orders_api import admin_orders_api_bp
from .admin.admin_users_api import admin_users_api_bp

__all__ = [
    # Core
    "listings_api_bp",
    "orders_api_bp",
    "users_api_bp",
    # Admin
    "admin_listings_api_bp",
    "admin_orders_api_bp",
    "admin_users_api_bp",
]
