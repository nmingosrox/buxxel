$(document).ready(function() {
    $('#logout-btn').on('click', async function() {
        try {
            const { error } = await window.supabaseClient.auth.signOut();
            if (error) {
                console.error('Error logging out:', error);
                alert('Failed to log out. Please try again.');
            } else {
                alert('You have been logged out.');
                location.reload();
            }
        } catch (err) {
            console.error("Unexpected logout error:", err);
            alert("Logout failed. Please try again.");
        }
    });
});
