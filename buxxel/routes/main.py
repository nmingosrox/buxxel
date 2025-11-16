from flask import Blueprint, render_template
from buxxel.extensions import supabase
from collections import defaultdict

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Renders the home page by fetching listings from Supabase."""
    # We render the first page of listings on the server for faster initial load and better SEO.
    # Subsequent pages are loaded via the '/api/listings/paged' endpoint (infinite scroll).
    per_page = 12
    try:
        print("Fetching initial listings...")
        # Fetch the first page of all listings for the main grid
        listings_response = supabase.table('listings').select(
            "*, purveyors(name)",
            count='exact'
        ).order('created_at', desc=True).limit(per_page).execute()
        
        listings = listings_response.data
        total_listings = listings_response.count
        has_next = total_listings > per_page
        
        # --- Refactored Category Card Logic ---
        # 1. Fetch all categories
        categories_response = supabase.table('categories').select('id, name, slug').execute()
        categories = categories_response.data if categories_response.data else []
        
        # 2. Initialize the data structure for the template
        categories_with_listings = {cat['id']: {'name': cat['name'], 'slug': cat['slug'], 'listings': []} for cat in categories}

        # 3. Loop through each category to fetch its listings (N+1 query pattern)
        for cat_id in categories_with_listings.keys():
            listings_for_cat_response = supabase.table('listings').select(
                "id, name, image_urls, category_id"
            ).eq(
                'category_id', cat_id
            ).order(
                'created_at', desc=True
            ).limit(4).execute()

            if listings_for_cat_response.data:
                categories_with_listings[cat_id]['listings'] = listings_for_cat_response.data

        print(f"✅ Initial listings fetched. Count: {len(listings)}, Total: {total_listings}.")
        return render_template('index.html', listings=listings, has_next=has_next, categories_with_listings=categories_with_listings)

    except Exception as e:
        print(f"❌ Failed to connect to Supabase or fetch listings: {e}")
        print("   Please check your .env file and Supabase table permissions.")
        return render_template('index.html', listings=[], has_next=False, categories_with_listings={}, error="Could not connect to the database.")
    
