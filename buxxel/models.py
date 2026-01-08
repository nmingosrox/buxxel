from datetime import datetime
from buxxel.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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

    # Set password (hash before saving)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Verify password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --------------------
# Listing Model
# --------------------
class BaseListing(db.Model):
    __abstract__ = True   # not a real table, just a base

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

class Product(BaseListing):
    __tablename__ = "products"

    stock = db.Column(db.Integer, nullable=False, default=0)
    sku = db.Column(db.String(50), unique=True)  # optional product code
    weight = db.Column(db.Float)                 # shipping weight
    dimensions = db.Column(db.String(100))       # e.g. "10x20x5 cm"

class Service(BaseListing):
    __tablename__ = "services"

    duration = db.Column(db.Integer)             # e.g. hours or days
    location = db.Column(db.String(120))         # optional: where service is delivered
    availability = db.Column(db.String(50))      # e.g. "weekdays", "weekends"

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

    def __repr__(self):
        return f"<OrderItem {self.id} - Qty {self.quantity}>"
