from flask import Blueprint, render_template
from buxxel.database import supabase   # adjust import if supabase client lives elsewhere

# Define the blueprint
main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    """Renders the home page by fetching listings from Supabase."""
    per_page = 12
    try:
        print("Fetching first page of listings...")
        # Fetch the first 12 listings and also get the total count
        response = supabase.table("listings").select("*", count="exact").limit(per_page).execute()
        
        listings = response.data or []          # actual rows returned
        total_listings = response.count or 0    # total count of rows in table
        has_next = total_listings > per_page    # show "Load More" if more than one page

        print(f"✅ Listings fetched. Total: {total_listings}, showing {len(listings)}.")
        return render_template("index.html", listings=listings, has_next=has_next)
    except Exception as e:
        print(f"❌ Error fetching listings: {e}")
        return render_template("index.html", listings=[], has_next=False, error="Could not connect to the database.")
