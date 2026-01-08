from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from buxxel.models import User
from buxxel.extensions import db

users_bp = Blueprint("users_bp", __name__, url_prefix="/users")

# --------------------
# USER LOGIN
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
            return redirect(url_for("main.index"))

        flash("Invalid credentials", "danger")
        return redirect(url_for("main.index"))
    return render_template("login.html")

# --------------------
# USER REGISTRATION
# --------------------
@users_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not password:
            flash("Password is required", "danger")
            return redirect(url_for("main.index"))

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

        login_user(new_user)
        flash("Successfully registered", "success")
        return redirect(url_for("main.index"))

    # GET request → just render the form
    return render_template("register.html")
# --------------------
# USER LOGOUT
# --------------------
@users_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))
