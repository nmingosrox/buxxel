// auth.js
$(document).ready(function() {

    // --- SIGNUP ---
    $('#signupForm').on('submit', async function(event) {
        event.preventDefault();

        const form = $(this);
        const submitBtn = form.find('button[type="submit"]');
        const originalBtnHtml = submitBtn.html();
        const alertDiv = $('#signup-alert');

        const email = $('#signupEmail').val();
        const password = $('#signupPassword').val();
        const confirmPassword = $('#confirmPassword').val();

        if (password !== confirmPassword) {
            alertDiv.text('Passwords do not match.')
                .removeClass('alert-success')
                .addClass('alert-danger')
                .show();
            return;
        }

        submitBtn.prop('disabled', true).html(
            '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Signing Up...'
        );

        const { data, error } = await window.supabaseClient.auth.signUp({ email, password });

        if (error) {
            alertDiv.text(error.message).removeClass('alert-success').addClass('alert-danger').show();
        } else {
            alertDiv.text('Signup successful! Please check your email to verify your account.')
                .removeClass('alert-danger')
                .addClass('alert-success')
                .show();
            setTimeout(() => {
                $('#authModal').modal('hide');
                $('#signupForm')[0].reset();
                alertDiv.hide().text('');
            }, 4000);
        }
        submitBtn.prop('disabled', false).html(originalBtnHtml);
    });

    // --- LOGIN ---
    $('#loginForm').on('submit', async function(event) {
        event.preventDefault();

        const form = $(this);
        const submitBtn = form.find('button[type="submit"]');
        const originalBtnHtml = submitBtn.html();
        const alertDiv = $('#login-alert');

        const email = $('#loginIdentifier').val();
        const password = $('#loginPassword').val();

        submitBtn.prop('disabled', true).html(
            '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Logging In...'
        );

        const { data, error } = await window.supabaseClient.auth.signInWithPassword({ email, password });

        if (error) {
            alertDiv.text(error.message).removeClass('alert-success').addClass('alert-danger').show();
            submitBtn.prop('disabled', false).html(originalBtnHtml);
        } else {
            location.reload();
        }
    });

    // --- PASSWORD RESET FLOW ---
    $('#forgot-password-link').on('click', function(e) {
        e.preventDefault();
        $('#loginForm, #signup-view, hr.my-4').hide();
        $('#password-reset-view').show();
        $('#authModalLabel').text('Reset Password');
    });

    $('#back-to-login-link').on('click', function(e) {
        e.preventDefault();
        $('#password-reset-view').hide();
        $('#loginForm, #signup-view, hr.my-4').show();
        $('#authModalLabel').text('Login or Create an Account');
    });

    $('#resetPasswordRequestForm').on('submit', async function(e) {
        e.preventDefault();
        const email = $('#resetEmail').val();
        const alertDiv = $('#reset-request-alert');
        const submitBtn = $(this).find('button[type="submit"]');
        const originalBtnHtml = submitBtn.html();

        submitBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span> Sending...');

        const { error } = await window.supabaseClient.auth.resetPasswordForEmail(email, {
            redirectTo: `${window.location.origin}/reset-password`,
        });

        if (error) {
            alertDiv.text(error.message).removeClass('alert-success').addClass('alert-danger').show();
        } else {
            alertDiv.text('Password reset link sent! Please check your email.')
                .removeClass('alert-danger')
                .addClass('alert-success')
                .show();
        }
        submitBtn.prop('disabled', false).html(originalBtnHtml);
    });

    // --- NAVBAR AUTH STATE ---
    async function updateAuthState() {
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

            $('#create-listing-cta').attr('href', '#').on('click', function(e) {
                e.preventDefault();
                $('#auth-context-message')
                    .text('You must log in or sign up to create a listing.')
                    .show();
                const authModal = new bootstrap.Modal(document.getElementById('authModal'));
                authModal.show();
            });
        }
    }

    updateAuthState();

    // --- LOGOUT ---
    $('#logout-btn').on('click', async function() {
        const { error } = await window.supabaseClient.auth.signOut();
        if (error) {
            console.error('Error logging out:', error);
            alert('Failed to log out. Please try again.');
        } else {
            alert('You have been logged out.');
            location.reload();
        }
    });

    // --- RESET MODAL STATE ---
    $('#authModal').on('hidden.bs.modal', function () {
        $('#auth-context-message').hide().text('');
        $('#password-reset-view').hide();
        $('#loginForm, #signup-view, hr.my-4').show();
        $('#authModalLabel').text('Login or Create an Account');
        $('#reset-request-alert').hide().text('');
    });
});
