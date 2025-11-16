from flask import Blueprint, request, redirect, flash, jsonify, current_app
from buxxel.extensions import supabase
from buxxel.auth.decorators import auth_required
import os

admin_api_bp = Blueprint('admin_api', __name__, url_prefix='/api')

# Adds a new purveyor to the purveyors table in supabase
@admin_api_bp.route('/purveyors/add', methods=['POST'])
def add_purveyor():
    data = {
        "name": request.form.get("name"),
        "email": request.form.get("email"),
        "phone": request.form.get("phone"),
        "website": request.form.get("website"),
        "logo_url": request.form.get("logo_url"),
        "description": request.form.get("description"),
        "country": request.form.get("country"),
        "city": request.form.get("city"),
        "address": request.form.get("address"),
        "type": request.form.get("type"),
        "status": request.form.get("status"),
        "is_verified": bool(request.form.get("is_verified")),
    }

    response = supabase.table("purveyors").insert(data).execute()

    if response.data:
        return "Successfully added purveyor"
    else:
        return f"Failed to add purveyor: {response}", "danger"

    return redirect("/admin")

# Deletes a purveyor from the purveyors table in supabase
@admin_api_bp.route('/purveyors/<purveyor_id>/delete', methods=['POST'])
def delete_purveyor_api(purveyor_id):
    response = supabase.table("purveyors").delete().eq("id", purveyor_id).execute()

    if response.data:
        return jsonify({"message": "Purveyor deleted successfully."}), 200
    else:
        return jsonify({"error": "Failed to delete purveyor."}), 400

from flask import request, jsonify

@admin_api_bp.route('/purveyors/<purveyor_id>/edit', methods=['POST'])
def edit_purveyor_api(purveyor_id):
    # Collect form data
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    website = request.form.get("website")
    country = request.form.get("country")
    city = request.form.get("city")
    address = request.form.get("address")
    purveyor_type = request.form.get("type")
    status = request.form.get("status")
    is_verified = request.form.get("is_verified") == "true"
    description = request.form.get("description")

    # Build update dictionary
    update_data = {
        "name": name,
        "email": email,
        "phone": phone,
        "website": website,
        "country": country,
        "city": city,
        "address": address,
        "type": purveyor_type,
        "status": status,
        "is_verified": is_verified,
        "description": description
    }

    # Remove None values so they don't overwrite existing fields
    update_data = {k: v for k, v in update_data.items() if v is not None}

    # Update in Supabase
    response = supabase.table("purveyors").update(update_data).eq("id", purveyor_id).execute()

    if response.data:
        return jsonify({"message": "Purveyor updated successfully.", "purveyor": response.data[0]}), 200
    else:
        return jsonify({"error": "Failed to update purveyor."}), 400

# Adds new listing to listings table in supabase
@admin_api_bp.route('/purveyor/<purveyor_id>/listings/add_listing', methods=['POST'])
def create_listing(purveyor_id):
    try:
        data = request.form

        # Required fields
        if not all([data.get('name'), data.get('price'), data.get('description'), data.get('image_url'), data.get('category_id')]):
            return jsonify({"error": "Missing required listing data."}), 400

        price = float(data.get('price'))
        final_price = price * (1 + current_app.config['COMMISSION_RATE'])

        # Stock only applies if category is a product-type category
        stock = int(data.get('stock')) if data.get('stock') else 0

        tags = [tag.strip().lower() for tag in data.get('tags', '').split(',') if tag.strip()]

        listing_data = {
            "name": data.get('name'),
            "price": final_price,
            "image_urls": [data.get('image_url')],
            "category_id": data.get('category_id'),   # ✅ use category_id instead of category name
            "description": data.get('description'),
            "stock": stock,            "purveyor_id": purveyor_id
        }

        response = supabase.table('listings').insert(listing_data).execute()
        return jsonify(response.data[0]), 201

    except (ValueError, TypeError):
        return jsonify({"error": "Price and stock must be valid numbers."}), 400
    except Exception as e:
        current_app.logger.error(f"Listing creation error: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred during listing creation."}), 500

# Edits an existing listing in supabase
@admin_api_bp.route('purveyor/<purveyor_id>/listings/<listing_id>/edit', methods=['POST'])
def edit_listing(purveyor_id, listing_id):
    try:
        data = request.form

        # Validate required fields
        if not all([data.get('name'), data.get('price'), data.get('description'), data.get('category_id')]):
            return jsonify({"error": "Missing required listing data."}), 400

        price = float(data.get('price'))
        final_price = price * (1 + current_app.config['COMMISSION_RATE'])
        stock = int(data.get('stock')) if data.get('stock') else 0

        update_data = {
            "name": data.get('name'),
            "price": final_price,
            "description": data.get('description'),
            "category_id": data.get('category_id'),
            "stock": stock,
        }

        # Optional image update
        if data.get('image_url'):
            update_data["image_urls"] = [data.get('image_url')]

        response = supabase.table("listings").update(update_data).eq("id", listing_id).eq("purveyor_id", purveyor_id).execute()

        if response.data:
            return jsonify(response.data[0]), 200
        else:
            return jsonify({"error": "Listing not found or update failed."}), 404

    except (ValueError, TypeError):
        return jsonify({"error": "Price and stock must be valid numbers."}), 400
    except Exception as e:
        current_app.logger.error(f"Listing edit error: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred during listing update."}), 500

@admin_api_bp.route('/purveyor/<purveyor_id>/listings/<listing_id>/delete', methods=['POST'])
def delete_listing(purveyor_id, listing_id):
    try:
        # Attempt to delete the listing for this purveyor
        response = supabase.table("listings") \
            .delete() \
            .eq("id", listing_id) \
            .eq("purveyor_id", purveyor_id) \
            .execute()

        if response.data:
            return jsonify({"message": "Listing deleted successfully."}), 200
        else:
            return jsonify({"error": "Listing not found or already deleted."}), 404

    except Exception as e:
        current_app.logger.error(f"Listing delete error: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred during listing deletion."}), 500


# Adds a new category
@admin_api_bp.route('/categories/add', methods=['POST'])
def add_category():
    name = request.form.get("name")
    slug = request.form.get("slug")
    description = request.form.get("description")

    if not name or not slug:
        flash("Name and slug are required.", "warning")
        return redirect("/admin/categories")

    data = {
        "name": name,
        "slug": slug,
        "description": description
    }

    response = supabase.table("categories").insert(data).execute()

    if response.data:
        return "Category added successfully!", "success"
    else:
        return "Failed to add category.", f"danger:<br> {response.data}"
    return redirect("/admin/categories")

# Edit category
@admin_api_bp.route('/categories/edit/<category_id>', methods=['POST'])
def edit_category(category_id):
    name = request.form.get("name")
    slug = request.form.get("slug")
    description = request.form.get("description")

    if not name or not slug:
        flash("Name and slug are required.", "warning")
        return redirect("/admin/categories")

    data = {
        "name": name,
        "slug": slug,
        "description": description
    }

    # Update instead of insert
    response = supabase.table("categories").update(data).eq("id", category_id).execute()

    if response.data:
        flash("Category updated successfully!", "success")
    else:
        flash(f"Failed to update category. Details: {response}", "danger")

    return redirect("/admin/categories")

# Delete category
@admin_api_bp.route('/categories/delete/<string:category_id>', methods=['POST'])
def delete_category(category_id):
    try:
        # Attempt to delete the category by its UUID
        response = supabase.table("categories").delete().eq("id", category_id).execute()

        if response.data:
            flash("Category deleted successfully!", "success")
        else:
            flash("Failed to delete category. Category not found.", "danger")

    except Exception as e:
        flash(f"Error deleting category: {str(e)}", "danger")

    return redirect("/admin/categories")
