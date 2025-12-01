$(document).ready(function() {
    const cart = JSON.parse(localStorage.getItem('buxxelCart')) || {};

    function populateCheckoutSummary() {
        const itemList = $('#checkout-item-list');
        const countBadge = $('#checkout-cart-count');

        itemList.empty(); // Clear loading state

        let totalItems = 0;
        let totalPrice = 0; // Initialize total price

        if (Object.keys(cart).length === 0) {
            // If cart is empty, redirect to home page as there's nothing to check out.
            window.location.href = '/';
            return;
        }

        for (const id in cart) {
            const item = cart[id];
            totalItems += item.quantity;

            const itemHtml = `
                <li class="list-group-item d-flex justify-content-between lh-sm">
                    <div>
                        <h6 class="my-0">${item.name}</h6>
                        <small class="text-muted">Quantity: ${item.quantity}</small>
                    </div>
                    <span class="text-muted">N$${(item.price * item.quantity).toFixed(2)}</span>
                </li>
            `;
            itemList.append(itemHtml);
            // Calculate total price inside the loop
            totalPrice += item.price * item.quantity;
        }

        // Add the total price to the list
        const totalHtml = `
            <li class="list-group-item d-flex justify-content-between">
                <span>Total (NAD)</span>
                <strong>N$${totalPrice.toFixed(2)}</strong>
            </li>
        `;
        itemList.append(totalHtml);

        countBadge.text(totalItems);
    }

    // Handle the form submission
    $('#checkout-form').on('submit', async function(e) {
        e.preventDefault();

        // Basic form validation check
        if (this.checkValidity() === false) {
            e.stopPropagation();
            $(this).addClass('was-validated');
            return;
        }
        $(this).addClass('was-validated');

        const submitBtn = $('#complete-purchase-btn');
        submitBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Placing Order...');

        // Calculate total price from the cart to ensure accuracy
        let totalPrice = 0;
        for (const id in cart) {
            totalPrice += cart[id].price * cart[id].quantity;
        }

        // Prepare the payload for the backend
        const payload = {
            shipping_address: {
                fullName: $('#fullName').val(),
                email: $('#email').val(),
                address: $('#address').val(),
                address2: $('#address2').val(),
                country: $('#country').val(),
                state: $('#state').val(),
                zip: $('#zip').val()
            },
            order_details: cart,
            total_price: totalPrice
        };

        try {
            const { data: sessionData, error: sessionError } = await window.supabaseClient.auth.getSession();
            if (sessionError || !sessionData.session) {
                throw new Error("You must be logged in to place an order.");
            }
            const token = sessionData.session.access_token;

            const response = await fetch('/api/orders', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to place order.');
            }

            // Clear the cart from localStorage
            localStorage.removeItem('buxxelCart');
            // Redirect to a success page
            window.location.href = '/order-success';
        } catch (error) {
            console.error("Order submission error:", error);
            alert(`Error: ${error.message}`);
            submitBtn.prop('disabled', false).html('Place Order');
        }
    });

    // Initial population of the checkout summary
    populateCheckoutSummary();
});