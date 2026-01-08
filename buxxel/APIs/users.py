from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from buxxel.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from buxxel.models import User
from buxxel import db
from werkzeug.security import check_password_hash, generate_password_hash
from buxxel.extensions import db

users_bp = Blueprint("users_bp", __name__, url_prefix="/users")

@users_bp.route("/login", methods=["GET", "POST"])
def login_view():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)

            # Redirect based on role
            if user.is_admin:
                return redirect(url_for("admin.index"))
            else:
                return redirect(url_for("main.index"))  # or your shop homepage

        flash("Invalid credentials")
    return render_template("login.html")

# --------------------
# LOGIN user
# --------------------
@users_bp.route("/login", methods=["POST", "GET"])
def login():
    print("attempting login")
    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("No Account found with that email, please register first", "warning")
        return redirect(url_for("main.index"))

    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        flash("Login Successful", "success")
        jsonify({"message": "Login successful", "user_id": user.id})
        return redirect(url_for("main.index"))
    flash("invalid password. Please try again", "danger")
    return redirect(url_for("main.index"))

# --------------------
# REGISTER user
# --------------------
@users_bp.route("/register", methods=["POST"])
def register_user():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    # Check if email already exists
    if User.query.filter_by(email=email).first():
        jsonify({"message": "Email already registered"}), 400

        flash("Email already registered please login", "primary")
        return redirect(url_for("main.index"))
    # Create new user
    new_user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)  # auto-login after registration
    jsonify({"message": "Registration successful", "user_id": new_user.id})
    flash("Succesfully Registered", "success")
    return redirect(url_for("main.index"))

# --------------------
# GET all users
# --------------------
@users_bp.route("/", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "is_admin": u.is_admin
    } for u in users])


# --------------------
# GET single user
# --------------------
@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin
    })


# --------------------
# CREATE new user
# --------------------
@users_bp.route("/", methods=["POST"])
def create_user():
    data = request.get_json()
    hashed_pw = generate_password_hash(data.get("password"))

    new_user = User(
        username=data.get("username"),
        email=data.get("email"),
        password_hash=hashed_pw,
        is_admin=data.get("is_admin", False)
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created", "id": new_user.id}), 201


# --------------------
# UPDATE user
# --------------------
@users_bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)
    if data.get("password"):
        user.password_hash = generate_password_hash(data["password"])
    user.is_admin = data.get("is_admin", user.is_admin)

    db.session.commit()
    return jsonify({"message": "User updated"})


# --------------------
# DELETE user
# --------------------
@users_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})


# --------------------
# LOGIN user
# --------------------
@users_bp.route("/login", methods=["POST"])
def login_user_api():
    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({"message": "Login successful", "user_id": user.id})
    return jsonify({"message": "Invalid email or password"}), 401


# --------------------
# REGISTER user
# --------------------
@users_bp.route("/register", methods=["POST"])
def register_user_api():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    # Check if email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400

    # Create new user
    new_user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)  # auto-login after registration
    return jsonify({"message": "Registration successful", "user_id": new_user.id})
