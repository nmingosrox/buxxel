async function updateAuthState() {
    try {
        const { data, error } = await window.supabaseClient.auth.getSession();
        if (error) {
            console.error("Error getting session:", error);
            return;
        }
        const session = data.session;
        const guestCtaSection = $('#guest-cta-section');

        if (session && session.user) {
            $('#auth-guest').addClass('d-none');
            $('#auth-user').removeClass('d-none').addClass('d-flex');
            $('#user-email').text(session.user.email);
            guestCtaSection.hide();

            const ADMIN_USER_ID = "34e36729-1ef1-4838-85b3-fc7e0456b341";
            if (session.user.id === ADMIN_USER_ID) {
                $('#admin-link').removeClass('d-none');
            }
        } else {
            $('#auth-guest').removeClass('d-none').addClass('d-flex');
            $('#auth-user').addClass('d-none');
            guestCtaSection.show();

            $('#create-listing-cta').off('click').on('click', function(e) {
                e.preventDefault();
                $('#auth-context-message')
                    .text('You must log in or sign up to create a listing.')
                    .show();
                const authModal = new bootstrap.Modal(document.getElementById('authModal'));
                authModal.show();
            });
        }
    } catch (err) {
        console.error("Unexpected auth state error:", err);
    }
}

$(document).ready(updateAuthState);
