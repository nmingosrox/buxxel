from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash
from buxxel.models import User
from buxxel.extensions import db

users_bp = Blueprint("users_bp", __name__, url_prefix="/users")

# --------------------
# USER LOGIN (form)
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
            # Admins will see the admin link in the template.
            return redirect(url_for("main.index"))

        flash("Invalid credentials", "danger")
        return redirect(url_for("main.index"))

    return render_template("login.html")


# --------------------
# ADMIN LOGIN (form, optional)
# --------------------
@users_bp.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email, is_admin=True).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Welcome Admin", "success")
            return redirect(url_for("main.index"))

        flash("Invalid admin credentials", "danger")
        return redirect(url_for("users_bp.admin_login"))

    return render_template("admin_login.html")


# --------------------
# USER REGISTRATION (form)
# --------------------
@users_bp.route("/register", methods=["POST"])
def register_user():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    if User.query.filter_by(email=email).first():
        flash("Email already registered, please login", "warning")
        return redirect(url_for("main.index"))

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


# --------------------
# USER LOGIN (API JSON)
# --------------------
@users_bp.route("/login_api", methods=["POST"])
def login_user_api():
    email = request.form.get("email")
    password = request.form.get("password")
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({"message": "Login successful", "user_id": user.id, "is_admin": user.is_admin})
    return jsonify({"message": "Invalid email or password"}), 401


# --------------------
# USER REGISTRATION (API JSON)
# --------------------
@users_bp.route("/register_api", methods=["POST"])
def register_user_api():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400

    new_user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)
    return jsonify({"message": "Registration successful", "user_id": new_user.id, "is_admin": new_user.is_admin})


# --------------------
# GET all users (API)
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
# GET single user (API)
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
# CREATE new user (API)
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
# UPDATE user (API)
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
# DELETE user (API)
# --------------------
@users_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})        password = request.form.get("password")
        user = User.query.filter_by(email=email, is_admin=True).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Welcome Admin", "success")
            return redirect(url_for("admin.index"))

        flash("Invalid admin credentials", "danger")
        return redirect(url_for("users_bp.admin_login"))

    return render_template("admin_login.html")


# --------------------
# USER REGISTRATION (form)
# --------------------
@users_bp.route("/register", methods=["POST"])
def register_user():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    if User.query.filter_by(email=email).first():
        flash("Email already registered, please login", "warning")
        return redirect(url_for("main.index"))

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


# --------------------
# USER LOGIN (API JSON)
# --------------------
@users_bp.route("/login_api", methods=["POST"])
def login_user_api():
    email = request.form.get("email")
    password = request.form.get("password")
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({"message": "Login successful", "user_id": user.id})
    return jsonify({"message": "Invalid email or password"}), 401


# --------------------
# USER REGISTRATION (API JSON)
# --------------------
@users_bp.route("/register_api", methods=["POST"])
def register_user_api():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400

    new_user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)
    return jsonify({"message": "Registration successful", "user_id": new_user.id})


# --------------------
# GET all users (API)
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
# GET single user (API)
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
# CREATE new user (API)
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
# UPDATE user (API)
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
# DELETE user (API)
# --------------------
@users_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})
