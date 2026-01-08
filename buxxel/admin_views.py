# buxxel/admin_views.py
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for

class SecureModelView(ModelView):
    def is_accessible(self):
        # Only allow logged-in admins
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # Redirect to login page if not accessible
        return redirect(url_for("users_bp.login"))


class ListingAdminView(SecureModelView):
    """Custom admin view for Listings."""

    # Columns to show in the list view
    column_list = ("id", "title", "price", "created_at")

    # Columns searchable
    column_searchable_list = ("title", "description")

    # Columns filterable
    column_filters = ("price", "created_at")

    # Labels for readability
    column_labels = {
        "title": "Listing Title",
        "price": "Price (NAD)",
        "created_at": "Date Created",
    }

    # Default sort
    column_default_sort = ("created_at", True)  # True = descending
