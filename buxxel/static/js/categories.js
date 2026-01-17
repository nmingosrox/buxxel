// categories.js
$(document).ready(function() {
    function loadCategories() {
        // collect categories container from DOM
        const container = $('#categories-container');
        // set maximum number of categories to display
        const LIMIT = 15; 
        // if the categories container doesn't exist stop
        if (!container.length) return; 

        // make backend call to Flask API route
        $.ajax({
            url: '/api/categories/popular',
            type: 'GET',
            success: function(categories) {
                // clear out any container content
                container.empty();

                // add an "All" button first
                const allButton = $('<button>', {
                    class: 'btn btn-secondary categories-btn active',
                    'data-category': 'all',
                    text: 'All'
                });
                container.append(allButton);

                // Limit the number of categories displayed
                const limitedCategories = categories.slice(0, LIMIT);
                limitedCategories.forEach(categoryInfo => {
                    const categoryButton = $('<button>', {
                        class: 'btn btn-outline-secondary categories-btn',
                        'data-category': categoryInfo.category,
                        text: categoryInfo.category
                    });
                    container.append(categoryButton);
                });
            },
            error: function() {
                container.html('<span class="text-danger">Could not load categories.</span>');
            }
        });
    }

    // Initialize on page load
    loadCategories();
});
