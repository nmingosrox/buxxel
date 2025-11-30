from functools import wraps
from flask import request, jsonify, current_app, redirect, url_for, flash
from gotrue.errors import AuthApiError
from buxxel.extensions import supabase
from buxxel.extensions import supabase_admin

def auth_required(f):
    """
    A decorator to protect routes with JWT authentication.
    It expects a 'Bearer <token>' in the 'Authorization' header,
    validates the token with Supabase, and passes the resulting user object to the decorated function.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authorization header is missing."}), 401
        
        parts = auth_header.split()

        if parts[0].lower() != 'bearer' or len(parts) != 2:
            return jsonify({"error": "Authorization header must be in the format 'Bearer <token>'."}), 401

        jwt = parts[1]
        try:
            user_response = supabase.auth.get_user(jwt)
            user = user_response.user
            if not user:
                return jsonify({"error": "Invalid or expired token."}), 401
        except AuthApiError as e:
            return jsonify({"error": f"Authentication error: {e.message}"}), 401
        except Exception as e:
            current_app.logger.error(f"Unexpected error during token validation: {e}")
            return jsonify({"error": "An unexpected error occurred during authentication."}), 500

        # Pass the user object to the decorated function
        return f(user, *args, **kwargs)
    return decorated_function

def page_auth_required(f):
    """
    A decorator to protect server-rendered pages.
    It checks for a Supabase session cookie, validates it, and passes the user object.
    If the user is not authenticated, it redirects them to the home page with a message.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Supabase stores the JWT in a cookie. The key is prefixed.
        # We need to find the cookie that contains the auth token.
        auth_cookie = next((value for key, value in request.cookies.items() if key.startswith('sb-') and key.endswith('-auth-token')), None)

        if not auth_cookie:
            flash("You must be logged in to view this page.", "warning")
            return redirect(url_for('main.index'))

        try:
            # The cookie value is a JSON string, we need to parse the access_token from it.
            import json
            jwt = json.loads(auth_cookie)['access_token']
            user_response = supabase.auth.get_user(jwt)
            user = user_response.user
        except (Exception, AuthApiError):
            flash("Your session has expired. Please log in again.", "warning")
            return redirect(url_for('main.index'))

        return f(user, *args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    A decorator to protect admin-only server-rendered pages.
    It checks for a valid session and that the user's profile has the 'admin' role.
    """
    # --- MVP SIMPLIFICATION ---
    # For an MVP, we can hardcode the admin's user ID to avoid database lookups.
    # Replace this with your actual Supabase User ID.
    ADMIN_USER_ID = "34e36729-1ef1-4838-85b3-fc7e0456b341"

    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_cookie = next((value for key, value in request.cookies.items() if key.startswith('sb-') and key.endswith('-auth-token')), None)

        if not auth_cookie:
            flash("You must be logged in to view this page.", "warning")
            return redirect(url_for('main.index'))
        try:
            import json
            jwt = json.loads(auth_cookie)['access_token']
            user_response = supabase.auth.get_user(jwt) # Use the standard client to validate the user
            user = user_response.user
        except (Exception, AuthApiError):
            flash("Your session has expired or is invalid. Please log in again.", "warning")
            return redirect(url_for('main.index'))

        # Instead of checking a role in the database, just check if the user's ID matches the admin ID.
        if str(user.id) != ADMIN_USER_ID:
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for('dashboard.dashboard'))

        # If all checks pass, proceed to the decorated function.
        return f(user, *args, **kwargs)
    return decorated_function