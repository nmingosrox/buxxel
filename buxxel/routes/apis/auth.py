from flask import Blueprint, request, jsonify
from buxxel.database import supabase  # using the standard client
import os

auth = Blueprint("auth", __name__)

@auth.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
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


@auth.route("/auth/signup", methods=["POST"])
def signup():
    data = request.form

    name = data.get('name')
    phone = data.get('phone')
    email = data.get("email")
    password = data.get("password")

    sburl = os.environ.get('SB_URL')
    print(sburl)
    response = supabase.auth.sign_up({
      "email":email, "password":password
      })

    return jsonify(response)
