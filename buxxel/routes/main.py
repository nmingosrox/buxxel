from flask import Blueprint, render_template, request, redirect, jsonify, url_for
from buxxel.extensions import supabase
from collections import defaultdict
import datetime, json, os
from twilio.rest import Client

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
    
@main_bp.route('/checkout/', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # Collect form data
        customer_name = request.form['fullName']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        city = request.form['city']
        postal_code = request.form['postalCode']
        preferred_contact = request.form['preferredContact']
        notes = request.form.get('notes')

        # Cart/session data
        order_items = request.form.get('order_items')  # JSON string
        total_price = float(request.form.get('total_price', 0.0))

        # Insert into Supabase
        response = supabase.table('orders').insert({
            "customer_name": customer_name,
            "customer_email": email,
            "customer_phone": phone,
            "customer_address": address,
            "customer_city": city,
            "customer_preferred_contact": preferred_contact,
            "customer_notes": notes,
            "order_items": order_items,
            "total_price": total_price,
            "status": "pending",
            "created_at": datetime.datetime.now().isoformat()
        }).execute()

        return render_template( 'checkout_success.html',
                               order_items=json.loads(order_items),
                               total_price=total_price
)

        # return redirect(url_for('main.checkout_success'))
    else:
        # Handle GET: show checkout page with cart summary
        order_items = request.args.get('order_items')
        total_price = request.args.get('total_price')
        return render_template('checkout.html',
                               order_items=order_items,
                               total_price=total_price)
    return render_template('checkout.html')

@main_bp.route('/checkout/success')
def checkout_success():
    # Retrieve order details
    order_items = request.args.get('order_items')  # JSON string
    total_price = request.args.get('total_price')
    customer_name = request.args.get('fullName')
    email = request.args.get('email')
    phone = request.args.get('phone')
    address = request.args.get('address')
    city = request.args.get('city')
    postal_code = request.args.get('postalCode')
    preferred_contact = request.args.get('preferredContact')
    notes = request.args.get('notes')

    items = json.loads(order_items) if order_items else {}

    # --- Twilio Messaging ---
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    twilio_number = os.environ.get("TWILIO_PHONE_NUMBER")
    my_number = os.environ.get("MY_PHONE_NUMBER")

    client = Client(account_sid, auth_token)

    # Build message body
    message_body = f"""
    New Order Received!
    Customer: {customer_name}
    Email: {email}
    Phone: {phone}
    Address: {address}, {city}, {postal_code}
    Preferred Contact: {preferred_contact}
    Notes: {notes or 'None'}

    Items:
    """
    for id, item in items.items():
        message_body += f"- {item['name']} x{item['quantity']} (${item['price']:.2f} each)\n"

    message_body += f"\nTotal: ${total_price}"

    # Send SMS
    client.messages.create(
        body=message_body,
        from_=twilio_number,
        to=my_number
    )

    # Render success page
    return render_template(
        'checkout_success.html',
        order_items=items,
        total_price=total_price,
        customer_name=customer_name,
        email=email,
        phone=phone,
        address=address,
        city=city,
        postal_code=postal_code,
        preferred_contact=preferred_contact,
        notes=notes
    )
