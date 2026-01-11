from flask import Blueprint, render_template
from buxxel.database import supabase   # updated import

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    """Renders the home page by fetching listings from Supabase."""
    per_page = 12
    try:
        # Check if there are any listings to determine if the "Load More" button should be shown.
        print("Checking for initial listings...")
        response = supabase.table("listings").select("id", count="exact").limit(1).execute()
        total_listings = response.count
        has_next = total_listings > 0

        print(f"✅ Initial listing check complete. Total: {total_listings}.")
        return render_template("index.html", has_next=has_next)

    except Exception as e:
        print(f"❌ Failed to connect to Supabase or fetch listings: {e}")
        print("   Please check your .env file and Supabase table permissions.")
        return render_template("index.html", has_next=False, error="Could not connect to the database.")
