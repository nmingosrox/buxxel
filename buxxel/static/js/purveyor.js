// purveyor.js
$(document).ready(function() {
    let purveyorButton = null;
    let originalButtonHtml = '';

    // Event delegation for "View Purveyor" button
    $('#listing-grid').on('click', '.view-purveyor-btn', function() {
        purveyorButton = $(this);
        const userId = purveyorButton.data('user-id');

        const modalElement = $('#purveyorProfileModal');
        const contentArea = modalElement.find('#purveyor-profile-content');
        const modalFooter = modalElement.find('.modal-footer');

        // Immediate feedback on button
        originalButtonHtml = purveyorButton.html();
        purveyorButton.prop('disabled', true).html(
            `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...`
        );

        // Show loading spinner in modal
        contentArea.html(`
            <div class="text-center p-4">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `);
        modalFooter.hide();

        // Fetch profile data
        $.ajax({
            url: `/api/profiles/${userId}`,
            type: 'GET',
            success: function(profile) {
                const profileHtml = `
                    <div class="text-center">
                        <i class="bi bi-shop-window fs-1 text-secondary mb-3"></i>
                        <h4 class="mb-1">${profile.username}</h4>
                        <p class="text-muted">Has ${profile.active_listings_count} active listings.</p>
                        <hr>
                        <p>What would you like to do?</p>
                        <a href="/profile/${profile.user_id}" class="btn btn-primary w-100 mb-2">
                            View All Listings by this Purveyor
                        </a>
                        <button class="btn btn-outline-secondary w-100" disabled>
                            Contact Purveyor (Coming Soon)
                        </button>
                    </div>
                `;
                contentArea.html(profileHtml);
                modalFooter.show();
            },
            error: function() {
                contentArea.html(`
                    <div class="alert alert-danger">
                        Could not load purveyor profile. Please try again later.
                    </div>
                `);
                modalFooter.show();
            },
            complete: function() {
                // Restore button state
                if (purveyorButton) {
                    purveyorButton.prop('disabled', false).html(originalButtonHtml);
                    purveyorButton = null;
                }
            }
        });
    });
});
