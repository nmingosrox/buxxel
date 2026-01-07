from flask import Blueprint, request, jsonify
from buxxel import db
from buxxel.models import Listing

# Create a blueprint for listings API
listings_bp = Blueprint("listings_api", __name__, url_prefix="/api/listings")

# --------------------
# GET all listings
# --------------------
@listings_bp.route("/", methods=["GET"])
def get_listings():
    listings = Listing.query.all()
    return jsonify([{
        "id": l.id,
        "title": l.title,
        "description": l.description,
        "price": l.price,
        "stock": l.stock,
        "created_at": l.created_at.isoformat()
    } for l in listings])


# --------------------
# GET single listing
# --------------------
@listings_bp.route("/<int:listing_id>", methods=["GET"])
def get_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    return jsonify({
        "id": listing.id,
        "title": listing.title,
        "description": listing.description,
        "price": listing.price,
        "stock": listing.stock,
        "created_at": listing.created_at.isoformat()
    })


# --------------------
# CREATE new listing
# --------------------
@listings_bp.route("/", methods=["POST"])
def create_listing():
    data = request.get_json()
    new_listing = Listing(
        title=data.get("title"),
        description=data.get("description"),
        price=data.get("price"),
        stock=data.get("stock", 0)
    )
    db.session.add(new_listing)
    db.session.commit()
    return jsonify({"message": "Listing created", "id": new_listing.id}), 201


# --------------------
# UPDATE listing
# --------------------
@listings_bp.route("/<int:listing_id>", methods=["PUT"])
def update_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    data = request.get_json()

    listing.title = data.get("title", listing.title)
    listing.description = data.get("description", listing.description)
    listing.price = data.get("price", listing.price)
    listing.stock = data.get("stock", listing.stock)

    db.session.commit()
    return jsonify({"message": "Listing updated"})


# --------------------
# DELETE listing
# --------------------
@listings_bp.route("/<int:listing_id>", methods=["DELETE"])
def delete_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    db.session.delete(listing)
    db.session.commit()
    return jsonify({"message": "Listing deleted"})
