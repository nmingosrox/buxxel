from flask_login import LoginManager
from flask_login import login_required, current_user
from flask import abort
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated and has an "admin" role
        if not current_user.is_authenticated or getattr(current_user, "role", None) != "admin":
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function


# Alias so your routes keep working
page_auth_required = login_required

login_manager = LoginManager()
