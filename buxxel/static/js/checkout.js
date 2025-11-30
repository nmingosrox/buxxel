$(document).ready(function() {
    const cart = JSON.parse(localStorage.getItem('buxxelCart')) || {};

    function populateCheckoutSummary() {
        const itemList = $('#checkout-item-list');
        const countBadge = $('#checkout-cart-count');
        const totalPriceEl = $('#checkout-total-price');

        itemList.empty(); // Clear loading state

        let totalItems = 0;
        let totalPrice = 0;

        if (Object.keys(cart).length === 0) {
            // If cart is empty, redirect to home page as there's nothing to check out.
            window.location.href = '/';
            return;
        }

        for (const id in cart) {
            const item = cart[id];
            totalItems += item.quantity;
            totalPrice += item.price * item.quantity;

            const itemHtml = `
                <li class="list-group-item d-flex justify-content-between lh-sm">
                    <div>
                        <h6 class="my-0">${item.name}</h6>
                        <small class="text-muted">Quantity: ${item.quantity}</small>
                    </div>
                    <span class="text-muted">$${(item.price * item.quantity).toFixed(2)}</span>
                </li>
            `;
            itemList.append(itemHtml);
        }

        // Add the total price to the list
        const totalHtml = `
            <li class="list-group-item d-flex justify-content-between">
                <span>Total (USD)</span>
                <strong>$${totalPrice.toFixed(2)}</strong>
            </li>
        `;
        itemList.append(totalHtml);

        countBadge.text(totalItems);
    }

    // Handle the form submission
    $('#checkout-form').on('submit', function(e) {
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

        // In a real application, you would send this data to a backend endpoint
        // to be processed and stored in a database.
        const orderDetails = {
            customer: {
                fullName: $('#fullName').val(),
                email: $('#email').val(),
                address: $('#address').val(),
                address2: $('#address2').val(),
                country: $('#country').val(),
                state: $('#state').val(),
                zip: $('#zip').val(),
            },
            items: cart,
            total: $('#checkout-total-price').text()
        };

        console.log("Simulating order submission with payload:", orderDetails);

        // Simulate a successful order placement
        setTimeout(() => {
            // Clear the cart from localStorage
            localStorage.removeItem('buxxelCart');

            // Redirect to a success page
            window.location.href = '/order-success';
        }, 1500);
    });

    // Initial population of the checkout summary
    populateCheckoutSummary();
});