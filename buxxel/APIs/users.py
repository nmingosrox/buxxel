from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from buxxel.models import User
from buxxel.extensions import db

users_bp = Blueprint("users_bp", __name__, url_prefix="/users")

# --------------------
# USER LOGIN (form via homepage modal)
# --------------------
@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Login successful", "success")
            # Both admins and normal users go to homepage.
            #the xheck for admin is done in the template
            # Admins will see the admin link in the template.
            return redirect(url_for("main.index"))

        flash("Invalid credentials", "danger")
        return redirect(url_for("main.index"))

# --------------------
# USER REGISTRATION (form via homepage modal)
# --------------------
@users_bp.route("/register", methods=["GET", "POST"])
def register():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    # Check if email already exists
    if User.query.filter_by(email=email).first():
        flash("Email already registered, please login", "primary")
        return redirect(url_for("main.index"))

    # Create new user with hashed password
    new_user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(new_user)
    db.session.commit()

    # Log the new user in immediately
    login_user(new_user)
    flash("Successfully registered", "success")
    return redirect(url_for("main.index"))
