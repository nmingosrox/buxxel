from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, flash, current_app
from buxxel.models import User, Listing, ListingImage
from buxxel.extensions import db, admin
from werkzeug.security import generate_password_hash
from markupsafe import Markup
from wtforms import PasswordField, StringField


class SecureModelView(ModelView):
    """Base admin view that restricts access to admins only."""

    # Inject Uploadcare widget script globally
    extra_js = [
        "https://ucarecdn.com/libs/widget/3.x/uploadcare.full.min.js"
    ]

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash("You must be an admin to access the admin panel.", "danger")
        return redirect(url_for("users_bp.login"))


class ListingImageAdmin(SecureModelView):
    """Standalone admin view for ListingImage (Uploadcare integration)."""

    column_list = ("id", "listing_id", "uploadcare_file")
    column_labels = {
        "uploadcare_file": "Uploadcare File UUID",
        "listing_id": "Listing",
    }

    form_overrides = {
        "uploadcare_file": StringField
    }

    def scaffold_form(self):
        """Attach Uploadcare widget attributes dynamically using config key."""
        form_class = super().scaffold_form()
        if hasattr(form_class, "uploadcare_file"):
            form_class.uploadcare_file.widget.attrs.update({
                "class": "uploadcare-uploader",
                "data-public-key": current_app.config.get("UPLOADCARE_PUBLIC_KEY", ""),
                "data-multiple": "true",
                "data-tabs": "file"  # restrict to local file uploads only
            })
        return form_class

    def _list_thumbnail(view, context, model, name):
        if not model.uploadcare_file:
            return ''
        return Markup(
            f'<img src="https://ucarecdn.com/{model.uploadcare_file}/-/resize/100x/" style="max-height:100px;">'
        )

    column_formatters = {
        "uploadcare_file": _list_thumbnail
    }


class ListingAdminView(SecureModelView):
    """Custom admin view for Listings with multiple images inline."""

    can_create = True
    can_edit = True
    can_delete = True

    column_list = ("id", "title", "price", "created_at", "type")
    column_searchable_list = ("title", "description")
    column_filters = ("price", "created_at", "type")

    column_labels = {
        "title": "Listing Title",
        "price": "Price (NAD)",
        "created_at": "Date Created",
        "type": "Listing Type",
    }

    column_default_sort = ("created_at", True)

    # Inline model for images with Uploadcare widget
    inline_models = [
        (ListingImage, {
            'form_overrides': {'uploadcare_file': StringField},
            'form_widget_args': {
                'uploadcare_file': {
                    'class': 'uploadcare-uploader',
                    'data-public-key': 'PLACEHOLDER_KEY',  # replaced at runtime
                    'data-multiple': 'true',
                    'data-tabs': 'file'  # restrict to local file uploads only
                }
            }
        })
    ]

    def scaffold_form(self):
        """Inject Uploadcare key at runtime inside app context."""
        form_class = super().scaffold_form()
        if hasattr(form_class, "uploadcare_file"):
            form_class.uploadcare_file.widget.attrs['data-public-key'] = \
                current_app.config.get("UPLOADCARE_PUBLIC_KEY", "")
        return form_class


class UserAdmin(SecureModelView):
    """Custom admin view for Users."""

    column_list = ("id", "username", "email", "is_admin")
    form_excluded_columns = ("password_hash",)

    form_extra_fields = {
        "password": PasswordField("Password")
    }

    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.password_hash = generate_password_hash(form.password.data)

    column_labels = {
        "is_admin": "Admin User",
    }
