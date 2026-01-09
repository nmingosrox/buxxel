from datetime import datetime
from buxxel.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# --------------------
# User Model
# --------------------
class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# --------------------
# Listing Base (real table, polymorphic)
# --------------------
class Listing(db.Model):
    __tablename__ = "listings"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # 'product' or 'service'
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    # Relationship to multiple images
    images = db.relationship(
        "ListingImage",
        backref="listing",
        lazy=True,
        cascade="all, delete-orphan"
    )

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "listing"
    }


class Product(Listing):
    __tablename__ = "products"

    id = db.Column(db.Integer, db.ForeignKey("listings.id"), primary_key=True)
    stock = db.Column(db.Integer, nullable=False, default=0)
    sku = db.Column(db.String(50), unique=True)
    weight = db.Column(db.Float)
    dimensions = db.Column(db.String(100))

    __mapper_args__ = {
        "polymorphic_identity": "product"
    }


class Service(Listing):
    __tablename__ = "services"

    id = db.Column(db.Integer, db.ForeignKey("listings.id"), primary_key=True)
    duration = db.Column(db.Integer)
    location = db.Column(db.String(120))
    availability = db.Column(db.String(50))

    __mapper_args__ = {
        "polymorphic_identity": "service"
    }


# --------------------
# ListingImage Model (NEW)
# --------------------
class ListingImage(db.Model):
    __tablename__ = "listing_images"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey("listings.id"), nullable=False)

    def __repr__(self):
        return f"<ListingImage {self.id} - {self.filename}>"


# --------------------
# Order Model
# --------------------
class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(50), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", lazy=True)

    def __repr__(self):
        return f"<Order {self.id} - {self.status}>"


# --------------------
# OrderItem Model
# --------------------
class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey("listings.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    listing = db.relationship("Listing", backref="order_items")

    def __repr__(self):
        return f"<OrderItem {self.id} - Qty {self.quantity}>"
