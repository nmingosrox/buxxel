from flask import Blueprint, render_template, request, redirect, jsonify, url_for
from buxxel.extensions import supabase
from collections import defaultdict
import datetime, json, os, smtplib
from flask import request, render_template
from twilio.rest import Client
from email.mime.text import MIMEText

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
    
import datetime, json, os, smtplib
from flask import request, render_template, redirect, url_for
from email.mime.text import MIMEText

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
        order_items = request.form.get('order_items')  # JSON string
        total_price = float(request.form.get('total_price', 0.0))

        # After inserting the order
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

        print(response)

        # Instead of relying on response.data[0]['id'], query the table for the latest order
        # latest = supabase.table('orders').select("id").order("created_at", desc=True).limit(1).execute()

        # order_id = latest.data[0]['id'] if latest.data else None

        # if order_id:        
        return redirect(url_for('main.checkout_success', order_id=order_id))
        # else:
            # return "Order creation failed", 400


    # GET: show checkout page
    order_items = request.args.get('order_items')
    total_price = request.args.get('total_price')
    return render_template('checkout.html',
                           order_items=order_items,
                           total_price=total_price)


@main_bp.route('/checkout/success')
def checkout_success():
    # order_id = request.args.get('order_id')
    # Fetch order from Supabase
    # response = supabase.table('orders').select("*").eq("id", order_id).execute()
    # order = response.data[0] if response.data else {}

    # Parse items safely
    # try:
        # items = json.loads(order.get("order_items", "{}"))
    # except Exception as e:
        # print(f"Error parsing order_items: {e}")
        # items = {}

    # Build message body
    # message_body = f"""
    # New Order Received!
    # Customer: {order.get('customer_name')}
    # Email: {order.get('customer_email')}
    # Phone: {order.get('customer_phone')}
    # Address: {order.get('customer_address')}, {order.get('customer_city')} {order.get('customer_postal_code')}
    # Preferred Contact: {order.get('customer_preferred_contact')}
    # Notes: {order.get('customer_notes') or 'None'}

    # Items:
    # """
    # for _, item in items.items():
        # message_body += f"- {item['name']} x{item['quantity']} (${item['price']:.2f} each)\n"
    # message_body += f"\nTotal: ${order.get('total_price')}"

    # Send email
    try:
        SMTP_HOST = "smtp.gmail.com"
        SMTP_PORT = 587
        SMTP_USER = os.environ.get("SMTP_USER")
        SMTP_PASS = os.environ.get("SMTP_PASS")

        msg = MIMEText("ther's a new order")
        msg["Subject"] = "New Order Notification"
        msg["From"] = SMTP_USER
        msg["To"] = SMTP_USER  # or order.get('customer_email') if you want to notify customer

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print("Email sent")
    except Exception as e:
        print(f"SMTP email failed: {e}")

    return render_template('checkout_success.html')#, order=order, items=items)
