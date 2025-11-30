from functools import wraps
from flask import request, jsonify, current_app
from gotrue.errors import AuthApiError
from buxxel.extensions import supabase

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