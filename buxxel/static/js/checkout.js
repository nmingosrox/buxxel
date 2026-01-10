$(document).ready(function() {
    const cart = JSON.parse(localStorage.getItem('buxxelCart')) || {};

    function populateCheckoutSummary() {
        const itemList = $('#checkout-item-list');
        const countBadge = $('#checkout-cart-count');

        itemList.empty(); // Clear loading state

        let totalItems = 0;
        let totalPrice = 0;

        if (Object.keys(cart).length === 0) {
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
            totalPrice += item.price * item.quantity;
        }

        const totalHtml = `
            <li class="list-group-item d-flex justify-content-between">
                <span>Total (NAD)</span>
                <strong>N$${totalPrice.toFixed(2)}</strong>
            </li>
        `;
        itemList.append(totalHtml);

        countBadge.text(totalItems);
    }

    // Show payment instructions dynamically
    function setupPaymentInstructions() {
        const paymentOptions = $('input[name="paymentMethod"]');
        const instructionsBox = $('<div>', {
            id: 'payment-instructions',
            class: 'alert alert-info mt-3'
        });
        $('#checkout-form').append(instructionsBox);

        paymentOptions.on('change', function() {
            let instructions = '';
            switch (this.id) {
                case 'eft':
                    instructions = `
                        <strong>EFT Instructions:</strong><br>
                        Bank: First National Bank Namibia<br>
                        Account: 123456789<br>
                        Branch Code: 280172<br>
                        Use your Order ID as reference.
                    `;
                    break;
                case 'ewallet':
                    instructions = `
                        <strong>Ewallet Instructions:</strong><br>
                        Send via MTC Ewallet to:<br>
                        Phone: +264 81 234 5678<br>
                        Reference: Your Order ID.
                    `;
                    break;
                case 'paypulse':
                    instructions = `
                        <strong>PayPulse Instructions:</strong><br>
                        Merchant number:<br>
                        +264 85 987 6543<br>
                        Reference: Your Order ID.
                    `;
                    break;
                case 'bluewallet':
                    instructions = `
                        <strong>BlueWallet Instructions:</strong><br>
                        Wallet ID: BUXXEL123<br>
                        Reference: Your Order ID.
                    `;
                    break;
                case 'banktransfer':
                    instructions = `
                        <strong>Bank Transfer Instructions:</strong><br>
                        Bank: Bank Windhoek<br>
                        Account: 987654321<br>
                        Branch Code: 481972<br>
                        Reference: Your Order ID.
                    `;
                    break;
            }
            instructionsBox.html(instructions);
        });
    }

    // Handle the form submission
    $('#checkout-form').on('submit', async function(e) {
        e.preventDefault();

        if (this.checkValidity() === false) {
            e.stopPropagation();
            $(this).addClass('was-validated');
            return;
        }
        $(this).addClass('was-validated');

        const submitBtn = $('#complete-purchase-btn');
        submitBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Placing Order...');

        let totalPrice = 0;
        for (const id in cart) {
            totalPrice += cart[id].price * cart[id].quantity;
        }

        const payload = {
            shipping_address: {
                fullName: $('#fullName').val(),
                email: $('#email').val(),
                address: $('#address').val(),
                address2: $('#address2').val(),
                country: $('#country-hidden').val(),
                region: $('#region').val(),
                zip: $('#zip').val()
            },
            order_details: cart,
            total_price: totalPrice,
            payment_method: $('input[name="paymentMethod"]:checked').attr('id') // capture selected payment method
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

            localStorage.removeItem('buxxelCart');
            window.location.href = '/order-success';
        } catch (error) {
            console.error("Order submission error:", error);
            alert(`Error: ${error.message}`);
            submitBtn.prop('disabled', false).html('Place Order');
        }
    });

    // Initialize
    populateCheckoutSummary();
    setupPaymentInstructions();
});
