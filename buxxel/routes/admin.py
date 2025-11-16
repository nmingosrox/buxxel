from flask import Blueprint, render_template
from buxxel.extensions import supabase

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def admin_dashboard():
    return render_template('admin/admin.html')

@admin_bp.route('/listings')
def admin_listings():
    # Fetch all listings and their associated category name
    listings_response = supabase.table("listings").select("*, categories(name)").order('created_at', desc=True).execute()
    listings = listings_response.data if listings_response.data else []

    # Fetch all categories to populate the dropdown in the edit modal
    categories_response = supabase.table("categories").select("id, name").order('name').execute()
    categories = categories_response.data if categories_response.data else []

    # Pass both listings and categories to the template
    return render_template('/admin/listings.html', listings=listings, categories=categories)


@admin_bp.route('/purveyors')
def admin_purveyors():
	purveyors_response = supabase.table("purveyors").select("*").execute()
	purveyors = purveyors_response.data if purveyors_response.data else []
	return render_template('/admin/purveyors.html', purveyors=purveyors)

@admin_bp.route('/categories')
def admin_categories():
	categories_response = supabase.table("categories").select("*").execute()
	categories = categories_response.data if categories_response.data else []
	return render_template('/admin/categories.html', categories=categories)


@admin_bp.route('/purveyors/<purveyor_id>')
def view_purveyor(purveyor_id):
    # get categories
    categories_response = supabase.table("categories").select("id, name").execute()
    categories = categories_response.data if categories_response.data else []
    # Get the purveyor record
    response = supabase.table("purveyors").select("*").eq("id", purveyor_id).single().execute()
    purveyor = response.data if response.data else None

    if not purveyor:
        flash("Purveyor not found.", "warning")
        return redirect("/admin/purveyors")

    # Get all listings for this purveyor
    listings_response = supabase.table("listings").select("*").eq("purveyor_id", purveyor_id).execute()
    listings = listings_response.data if listings_response.data else []

    # Pass both purveyor and listings to the template
    return render_template("admin/purveyor_view.html", purveyor=purveyor, listings=listings, categories=categories)

@admin_bp.route('/purveyors/<purveyor_id>/listings')
def purveyor_listings(purveyor_id):
    purveyor_resp = supabase.table("purveyors").select("*").eq("id", purveyor_id).single().execute()
    purveyor = purveyor_resp.data if purveyor_resp.data else None

    if not purveyor:
        flash("Purveyor not found.", "warning")
        return redirect("/admin/purveyors")

    listings_resp = supabase.table("listings").select("*").eq("purveyor_id", purveyor_id).execute()
    listings = listings_resp.data if listings_resp.data else []

    return render_template("admin/purveyor_listings.html", purveyor=purveyor, listings=listings)
