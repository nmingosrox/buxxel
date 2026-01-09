# buxxel/admin_views.py
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, flash
from buxxel.models import User
from buxxel.extensions import db, admin
from werkzeug.security import generate_password_hash

class SecureModelView(ModelView):
    """Base admin view that restricts access to admins only."""

    def is_accessible(self):
        # Only allow logged-in admins
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash("You must be an admin to access the admin panel.", "danger")
        return redirect(url_for("users_bp.login"))


class ListingAdminView(SecureModelView):
    """Custom admin view for Listings."""

    can_create = True
    can_edit = True
    can_delete = True

    column_list = ("id", "title", "price", "created_at")
    column_searchable_list = ("title", "description")
    column_filters = ("price", "created_at")

    column_labels = {
        "title": "Listing Title",
        "price": "Price (NAD)",
        "created_at": "Date Created",
    }

    column_default_sort = ("created_at", True)


class UserAdmin(SecureModelView):
    """Custom admin view for Users."""

    # Show only relevant fields
    column_list = ("id", "username", "email", "is_admin")

    # Don’t expose password_hash directly
    form_excluded_columns = ("password_hash",)

    # Add a custom form field for setting/resetting password
    form_extra_fields = {
        "password": db.Column(db.String(128))
    }

    def on_model_change(self, form, model, is_created):
        """Hash password if provided in the admin form."""
        if hasattr(form, "password") and form.password.data:
            model.password_hash = generate_password_hash(form.password.data)

    column_labels = {
        "is_admin": "Admin User",
    }
