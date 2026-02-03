from flask import Blueprint, request, jsonify
from buxxel.database import supabase
import os

api = Blueprint("api", __name__)

@api.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    try:
        # Supabase Auth sign-in
        result = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if result.user:
            # Return access token and user info
            return jsonify({
                "message": "Login successful",
                "user": {
                    "id": result.user.id,
                    "email": result.user.email
                },
                "access_token": result.session.access_token,
                "refresh_token": result.session.refresh_token
            }), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500
