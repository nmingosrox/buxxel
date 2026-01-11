// location.js
$(document).ready(function() {
    function loadUserLocation() {
        const locationDisplay = $('#location-display');
        if (!locationDisplay.length) return;

        $.ajax({
            url: 'http://ip-api.com/json',
            type: 'GET',
            success: function(response) {
                if (response && response.status === 'success' && response.city) {
                    const locationText = `Delivering to: ${response.city}, ${response.countryCode}`;
                    locationDisplay.text(locationText).removeClass('d-none');
                }
            },
            error: function() {
                // Fail silently if the API call doesn’t work
                console.log("Could not retrieve user location via IP.");
            }
        });
    }

    // Initialize on page load
    loadUserLocation();
});
