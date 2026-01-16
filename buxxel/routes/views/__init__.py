from .main import main_bp
from .dashboard import dashboard_bp
from .checkout import checkout_bp
from .admin import admin_bp

# If you add more page blueprints later, import them here too.
# Example:
# from .orders import orders_bp

# Collect all blueprints in a list for easy registration
__all__ = [
    main_bp,
    dashboard_bp,
    checkout_bp,
    admin_bp,
    # orders_bp,  # uncomment when you add orders routes
]
