document.addEventListener('DOMContentLoaded', function () {
    const tableBody = document.getElementById('listings-table-body');
    const loadingSpinner = document.getElementById('loading-spinner');
    const noListingsMessage = document.getElementById('no-listings-message');

    async function fetchAndRenderListings() {
        try {
            const response = await fetch('/admin/api/listings');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const listings = await response.json();

            loadingSpinner.style.display = 'none';
            tableBody.innerHTML = ''; // Clear existing rows

            if (listings.length === 0) {
                noListingsMessage.style.display = 'block';
            } else {
                listings.forEach(listing => {
                    const row = createListingRow(listing);
                    tableBody.appendChild(row);
                });
            }
        } catch (error) {
            console.error('Error fetching listings:', error);
            loadingSpinner.style.display = 'none';
            tableBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Failed to load listings. Please try again later.</td></tr>`;
        }
    }

    function createListingRow(listing) {
        const row = document.createElement('tr');

        const imageUrl = (listing.image_urls && listing.image_urls.length > 0)
            ? `${listing.image_urls[0]}-/preview/100x100/`
            : '/static/images/placeholder.png'; // Fallback image

        // Use textContent for safe data injection
        const imageCell = row.insertCell();
        imageCell.innerHTML = `<img src="${imageUrl}" alt="" class="img-thumbnail" style="width: 80px; height: 80px; object-fit: cover;">`;
        imageCell.querySelector('img').alt = listing.title;

        const titleCell = row.insertCell();
        titleCell.textContent = listing.title;

        const purveyorCell = row.insertCell();
        purveyorCell.textContent = listing.purveyor_name || 'N/A';

        const priceCell = row.insertCell();
        priceCell.textContent = `N$${parseFloat(listing.price).toFixed(2)}`;

        const actionsCell = row.insertCell();
        actionsCell.innerHTML = `
            <button class="btn btn-sm btn-outline-primary edit-listing-btn" title="Edit">
                <i class="bi bi-pencil-fill"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger delete-listing-btn" title="Delete" 
                    data-id="${listing.id}" 
                    data-image-urls='${JSON.stringify(listing.image_urls || [])}'>
                <i class="bi bi-trash-fill"></i>
            </button>
        `;

        return row;
    }

    // Event listener for delete buttons (using event delegation)
    tableBody.addEventListener('click', async function(event) {
        const deleteButton = event.target.closest('.delete-listing-btn');
        if (deleteButton) {
            const listingId = deleteButton.dataset.id;
            const imageUrls = JSON.parse(deleteButton.dataset.imageUrls); // Parse the JSON string back to an array

            if (confirm(`Are you sure you want to delete listing ID ${listingId}? This action cannot be undone.`)) {
                try {
                    deleteButton.disabled = true; // Disable button during operation
                    deleteButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';

                    const response = await fetch(`/admin/api/listings/${listingId}`, {
                        method: 'DELETE'
                    });

                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                    }

                    deleteButton.closest('tr').remove(); // Remove the row from the table
                    if (tableBody.children.length === 0) {
                        noListingsMessage.style.display = 'block';
                    }
                    alert('Listing and associated images deleted successfully!');
                } catch (error) {
                    console.error('Error deleting listing:', error);
                    alert(`Failed to delete listing: ${error.message}`);
                    deleteButton.disabled = false; // Re-enable button on error
                    deleteButton.innerHTML = '<i class="bi bi-trash-fill"></i>';
                }
            }
        }
    });

    // Initial fetch
    fetchAndRenderListings();
});