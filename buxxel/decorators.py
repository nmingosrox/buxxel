from functools import wraps
from flask import request, jsonify, redirect, url_for, flash
import json
from buxxel.database import supabase

# --- Basic API Auth ---
def auth_required(f):
    """
    Protect API routes with JWT authentication.
    Expects 'Authorization: Bearer <token>' header.
    Passes the user object to the decorated function.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401

        jwt = token.split(" ")[1]
        user_response = supabase.auth.get_user(jwt)
        if not user_response.user:
            return jsonify({"error": "Invalid or expired token"}), 401

        return f(user_response.user, *args, **kwargs)
    return decorated_function


# --- Basic Page Auth ---
def page_auth_required(f):
    """
    Protect server-rendered pages with Supabase session cookie.
    Redirects to home if not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        cookie = request.cookies.get("sb-access-token")
        if not cookie:
            flash("Please log in first.", "warning")
            return redirect(url_for("main.index"))

        try:
            jwt = json.loads(cookie)["access_token"]
            user_response = supabase.auth.get_user(jwt)
            if not user_response.user:
                flash("Session expired.", "warning")
                return redirect(url_for("main.index"))
        except Exception:
            flash("Authentication failed.", "warning")
            return redirect(url_for("main.index"))

        return f(user_response.user, *args, **kwargs)
    return decorated_function


# --- Simple Admin Check ---
ADMIN_USER_ID = "34e36729-1ef1-4838-85b3-fc7e0456b341"

def admin_required(f):
    """
    Restrict access to admin-only pages.
    Checks if user ID matches hardcoded admin ID.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        cookie = request.cookies.get("sb-access-token")
        if not cookie:
            flash("Admin login required.", "danger")
            return redirect(url_for("main.index"))

        jwt = json.loads(cookie)["access_token"]
        user_response = supabase.auth.get_user(jwt)
        user = user_response.user

        if not user or str(user.id) != ADMIN_USER_ID:
            flash("You do not have permission.", "danger")
            return redirect(url_for("main.index"))

        return f(user, *args, **kwargs)
    return decorated_function
