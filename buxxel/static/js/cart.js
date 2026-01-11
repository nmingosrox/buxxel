// cart.js
$(document).ready(function() {
    // --- CART STATE ---
    let cart = JSON.parse(localStorage.getItem('buxxelCart')) || {};

    // --- CORE FUNCTIONS ---
    function updateCart() {
        let totalItems = 0;
        let totalPrice = 0;
        const cartItemsContainer = $('#cart-items-container');
        cartItemsContainer.empty();
        const stickyFooter = $('#sticky-cart-footer');

        if (Object.keys(cart).length === 0) {
            cartItemsContainer.html('<p>Your cart is empty.</p>');
        } else {
            const itemList = $('<ul class="list-group"></ul>');
            for (const id in cart) {
                const item = cart[id];
                totalItems += item.quantity;
                totalPrice += item.price * item.quantity;

                const itemHtml = `
                    <li class="list-group-item d-flex justify-content-between align-items-center" data-id="${id}">
                        <div>
                            <h6 class="my-0">${item.name}</h6>
                            <small class="text-muted">Price: N$${item.price.toFixed(2)}</small>
                        </div>
                        <div class="d-flex align-items-center">
                            <button class="btn btn-sm btn-outline-secondary decrease-qty" data-id="${id}">-</button>
                            <span class="mx-2 cart-item-quantity">${item.quantity}</span>
                            <button class="btn btn-sm btn-outline-secondary increase-qty" data-id="${id}">+</button>
                            <button class="btn btn-sm btn-danger ms-3 remove-item" data-id="${id}" aria-label="Remove item">&times;</button>
                        </div>
                    </li>
                `;
                itemList.append(itemHtml);
            }
            cartItemsContainer.append(itemList);
        }

        $('#cart-count').text(totalItems);
        $('#cart-total').text(totalPrice.toFixed(2));

        // Sticky footer logic
        if (totalItems > 0) {
            $('#sticky-cart-info').text(`${totalItems} item${totalItems > 1 ? 's' : ''} in your cart`);
            $('#sticky-cart-total').text(`N$${totalPrice.toFixed(2)}`);
            stickyFooter.slideDown(function() {
                $('body').css('padding-bottom', stickyFooter.outerHeight() + 'px');
            });
        } else {
            stickyFooter.slideUp(function() {
                $('body').css('padding-bottom', '');
            });
        }
    }

    function saveCart() {
        localStorage.setItem('buxxelCart', JSON.stringify(cart));
    }

    // --- EVENT HANDLERS ---
    // Add to cart
    $('#listing-grid').on('click', '.add-to-cart-btn', function() {
        const button = $(this);
        const id = button.data('id');
        const name = button.data('name');
        const price = parseFloat(button.data('price'));

        if (cart[id]) {
            cart[id].quantity++;
        } else {
            cart[id] = { name: name, price: price, quantity: 1 };
        }

        updateCart();
        saveCart();

        // Visual feedback
        button.text('Added!').addClass('btn-success').removeClass('btn-warning');
        setTimeout(() => {
            button.text('Add to Cart').removeClass('btn-success').addClass('btn-warning');
        }, 1000);
    });

    // Increase quantity
    $('#cart-items-container').on('click', '.increase-qty', function() {
        const id = $(this).data('id');
        if (cart[id]) {
            cart[id].quantity++;
            updateCart();
            saveCart();
        }
    });

    // Decrease quantity
    $('#cart-items-container').on('click', '.decrease-qty', function() {
        const id = $(this).data('id');
        if (cart[id]) {
            cart[id].quantity--;
            if (cart[id].quantity <= 0) delete cart[id];
            updateCart();
            saveCart();
        }
    });

    // Remove item
    $('#cart-items-container').on('click', '.remove-item', function() {
        const id = $(this).data('id');
        if (cart[id]) {
            delete cart[id];
            updateCart();
            saveCart();
        }
    });

    // --- INIT ---
    updateCart();
});
