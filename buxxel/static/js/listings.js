// listings.js
$(document).ready(function() {
    const loadMoreContainer = document.getElementById('load-more-container');
    let observer;

    // --- LOAD MORE LISTINGS ---
    function loadMoreListings(isNewFilter = false) {
        const button = $('#load-more-btn');
        if (button.prop('disabled') && !isNewFilter) return;

        let nextPage;
        if (isNewFilter) {
            $('#listing-grid').empty();
            nextPage = 1;
            button.data('next-page', 1);
        } else {
            nextPage = button.data('next-page');
        }

        if (!nextPage) return;

        const originalHtml = button.html();
        button.prop('disabled', true).html(
            `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...`
        );

        const activeTag = $('.tag-btn.active').data('tag') || 'all';
        const rawSearch = $(window).width() < 992 ? $('#search-bar-mobile').val() : $('#search-bar-desktop').val();
        const searchTerm = (typeof rawSearch === 'string' ? rawSearch.trim() : '');

        $.ajax({
            url: `/api/listings/paged?page=${nextPage}&tag=${encodeURIComponent(activeTag)}&search=${encodeURIComponent(searchTerm)}`,
            type: 'GET',
            success: function(response) {
                const listings = response.listings;
                const pagination = response.pagination;

                if (listings && listings.length > 0) {
                    listings.forEach(listing => {
                        const imageUrl = (listing.image_urls && listing.image_urls.length > 0)
                            ? listing.image_urls[0]
                            : 'https://via.placeholder.com/300x200.png?text=No+Image';

                        const productCardHtml = `
<div class="col-lg-3 col-md-4 col-sm-6 listing-card" 
     data-tags="${(listing.tags || []).join(',')}" 
     data-name="${listing.name.toLowerCase()}"
     data-title="${listing.name}"
     data-description="${encodeURIComponent(listing.description || '')}"
     data-image="${imageUrl}"
     data-price="${listing.price}">
  <div class="card h-100 shadow-sm">
    <a href="#" class="listing-preview-trigger" data-bs-toggle="modal" data-bs-target="#listingPreviewModal">
      <img src="${imageUrl}" class="card-img-top" alt="${listing.name}" loading="lazy">
    </a>
    <div class="card-body d-flex flex-column">
      <h5 class="card-title">${listing.name}</h5>
      <p class="card-text fw-bold fs-5 mb-3">N$${Number(listing.price).toFixed(2)}</p>
      <div class="mt-auto d-grid">
        <button class="btn btn-warning add-to-cart-btn"
                data-id="${listing.id}"
                data-name="${listing.name}"
                data-price="${listing.price}">
          Add to Cart
        </button>
      </div>
    </div>
  </div>
</div>`;
                        $('#listing-grid').append(productCardHtml);
                    });
                } else if (isNewFilter) {
                    $('#listing-grid').html('<div class="text-center p-5 col-12"><h4 class="text-muted">No listings match your filters.</h4></div>');
                }

                if (pagination.has_next) {
                    button.data('next-page', pagination.page + 1);
                    button.prop('disabled', false).html(originalHtml);
                } else {
                    button.hide();
                    if (observer) observer.disconnect();
                }
            },
            error: function() {
                button.prop('disabled', false).html('Failed to load. Try again?');
            }
        });
    }

    // --- OBSERVER SETUP ---
    const loadMoreBtn = document.getElementById('load-more-btn');
    if (loadMoreContainer) {
        observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting && loadMoreBtn) {
                loadMoreListings(false);
            }
        }, { threshold: 1.0 });

        if (loadMoreBtn) observer.observe(loadMoreContainer);
        loadMoreListings(true);
    }

    // --- FILTERING ---
    $('#popular-tags-container').on('click', '.tag-btn', function() {
        $('.tag-btn').removeClass('active');
        $(this).addClass('active');
        loadMoreListings(true);
    });

    $('#search-bar-desktop, #search-bar-mobile').on('keyup', debounce(function() {
        const currentValue = $(this).val();
        $('#search-bar-desktop').val(currentValue);
        $('#search-bar-mobile').val(currentValue);
        loadMoreListings(true);
    }, 300));

    // --- DEBOUNCE UTILITY ---
    function debounce(func, delay) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), delay);
        };
    }

    // --- LISTING PREVIEW MODAL ---
    $('body').on('click', '.listing-preview-trigger', function(e) {
        e.preventDefault();
        const $card = $(this).closest('.listing-card');

        const title = $card.data('title') || 'Untitled Listing';
        const imageUrl = $card.data('image') || 'https://via.placeholder.com/300x200.png?text=No+Image';
        const price = $card.data('price');
        const descriptionRaw = decodeURIComponent($card.data('description') || '');

        $('#listingPreviewTitle').text(title);
        $('#listingPreviewImage').attr('src', imageUrl);

        const $detailsList = $('#listingPreviewDetails');
        $detailsList.empty();

        if (price) {
            $detailsList.append(`<li><strong>Price:</strong> N$${parseFloat(price).toFixed(2)}</li>`);
        }

        descriptionRaw.split(';').map(item => item.trim()).filter(Boolean).forEach(detail => {
            $detailsList.append(`<li>${detail}</li>`);
        });

        $('#listingPreviewModal').modal('show');
    });
});
