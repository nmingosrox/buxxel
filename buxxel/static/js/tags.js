// tags.js
$(document).ready(function() {
    function loadPopularTags() {
        const container = $('#popular-tags-container');
        const TAG_LIMIT = 15; // maximum number of tags to display
        if (!container.length) return;

        $.ajax({
            url: '/api/tags/popular',
            type: 'GET',
            success: function(tags) {
                container.empty();

                // Always add an "All" button first
                container.append('<button class="btn btn-secondary tag-btn active" data-tag="all">All</button>');

                // Limit the number of tags displayed
                const limitedTags = tags.slice(0, TAG_LIMIT);
                limitedTags.forEach(tagInfo => {
                    const tagButton = `
                        <button class="btn btn-outline-secondary tag-btn" data-tag="${tagInfo.tag}">
                            ${tagInfo.tag}
                        </button>
                    `;
                    container.append(tagButton);
                });
            },
            error: function() {
                container.html('<span class="text-danger">Could not load popular tags.</span>');
            }
        });
    }

    // Initialize on page load
    loadPopularTags();
});
