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
