$(document).ready(function() {
    const supabase = window.supabaseClient;

    // --- NEW LISTING FORM SUBMISSION ---
    $('#newListingForm').on('submit', async function(event) {
        event.preventDefault(); // Prevent the default browser form submission

        const form = $(this);
        const submitBtn = form.find('button[type="submit"]');
        const originalBtnHtml = submitBtn.html();
        const alertDiv = $('#new-listing-alert');

        submitBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Posting...');
        alertDiv.hide().removeClass('alert-danger alert-success');

        // 1. Get the current session token
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();

        if (sessionError || !session) {
            showAlert(alertDiv, 'Authentication error. Please log in again.', 'danger');
            submitBtn.prop('disabled', false).html(originalBtnHtml);
            // Optionally, redirect to login
            // window.location.href = '/login';
            return;
        }

        const token = session.access_token;

        // 2. Get the image URL from the Uploadcare widget
        const widget = uploadcare.Widget('#new-uploadcare-widget');
        const fileInfo = await widget.value();

        if (!fileInfo) {
            showAlert(alertDiv, 'Please upload a product image.', 'danger');
            submitBtn.prop('disabled', false).html(originalBtnHtml);
            return;
        }

        // --- Client-side validation ---
        const price = $('#newListingPrice').val();
        const stock = $('#newListingStock').val();

        if (price === '' || parseFloat(price) < 0) {
            showAlert(alertDiv, 'Please enter a valid, non-negative price.', 'danger');
            submitBtn.prop('disabled', false).html(originalBtnHtml);
            return;
        }
        if (stock === '' || parseInt(stock, 10) < 0) {
            showAlert(alertDiv, 'Please enter a valid, non-negative stock quantity.', 'danger');
            submitBtn.prop('disabled', false).html(originalBtnHtml);
            return;
        }

        // 3. Create FormData to send all data, including the file
        const formData = new FormData();
        formData.append('name', $('#newListingName').val());
        formData.append('price', $('#newListingPrice').val());
        formData.append('stock', $('#newListingStock').val());
        formData.append('description', $('#newListingDescription').val());
        formData.append('tags', $('#newListingTags').val());
        formData.append('image_url', fileInfo.cdnUrl); // Get the CDN URL

        // 4. Send the data using fetch with the Authorization header
        try {
            const response = await fetch(form.attr('action'), {
                method: 'POST',
                headers: {
                    // This is the crucial part that was missing
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            const result = await response.json();

            if (!response.ok) {
                // Handle errors from the server (e.g., validation errors)
                throw new Error(result.error || `HTTP error! status: ${response.status}`);
            }

            // Success!
            showAlert(alertDiv, 'Listing created successfully!', 'success');
            form[0].reset();
            widget.value(null); // Clear the Uploadcare widget

            setTimeout(() => {
                $('#newListingModal').modal('hide');
                // Here you would typically reload the listings on the dashboard
                // For now, we can just reload the page to see the new listing.
                location.reload();
            }, 2000);

        } catch (error) {
            console.error('Listing creation failed:', error);
            showAlert(alertDiv, error.message, 'danger');
        } finally {
            submitBtn.prop('disabled', false).html(originalBtnHtml);
        }
    });

    /**
     * Helper function to show alerts
     * @param {jQuery} alertDiv The jQuery object for the alert element.
     * @param {string} message The message to display.
     * @param {string} type 'success' or 'danger'.
     */
    function showAlert(alertDiv, message, type) {
        alertDiv
            .text(message)
            .removeClass('alert-success alert-danger')
            .addClass(`alert-${type}`)
            .show();
    }

});