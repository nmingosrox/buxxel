from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, flash
from buxxel.models import User, Listing
from buxxel.extensions import db, admin
from werkzeug.security import generate_password_hash
from flask_admin.form import ImageUploadField
from markupsafe import Markup
from wtforms import PasswordField
import os


class SecureModelView(ModelView):
    """Base admin view that restricts access to admins only."""

    def is_accessible(self):
        # Only allow logged-in admins
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash("You must be an admin to access the admin panel.", "danger")
        return redirect(url_for("users_bp.login"))


class ListingAdminView(SecureModelView):
    """Custom admin view for Listings with image support."""

    can_create = True
    can_edit = True
    can_delete = True

    column_list = ("id", "title", "price", "created_at", "image")
    column_searchable_list = ("title", "description")
    column_filters = ("price", "created_at", "type")

    column_labels = {
        "title": "Listing Title",
        "price": "Price (NAD)",
        "created_at": "Date Created",
        "image": "Listing Image",
        "type": "Listing Type",
    }

    column_default_sort = ("created_at", True)

    # Configure image upload
    form_extra_fields = {
        "image": ImageUploadField(
            "Listing Image",
            base_path=os.path.join(os.path.dirname(__file__), "..", "static", "uploads"),
            url_relative_path="uploads/"
        )
    }

    # Show thumbnails in list view
    def _list_thumbnail(view, context, model, name):
        if not model.image:
            return ''
        return Markup(f'<img src="/static/uploads/{model.image}" style="max-height:100px;">')

    column_formatters = {
        "image": _list_thumbnail
    }


class UserAdmin(SecureModelView):
    """Custom admin view for Users."""

    column_list = ("id", "username", "email", "is_admin")
    form_excluded_columns = ("password_hash",)

    # Add a custom form field for setting/resetting password
    form_extra_fields = {
        "password": PasswordField("Password")
    }

    def on_model_change(self, form, model, is_created):
        """Hash password if provided in the admin form."""
        if form.password.data:
            model.password_hash = generate_password_hash(form.password.data)

    column_labels = {
        "is_admin": "Admin User",
    }
