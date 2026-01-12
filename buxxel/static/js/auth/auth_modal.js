$(document).ready(function() {
    // --- RESET MODAL STATE ---
    $('#authModal').on('hidden.bs.modal', function () {
        // Hide and clear contextual message
        $('#auth-context-message').hide().text('');

        // Reset password reset view
        $('#password-reset-view').hide();

        // Show login/signup views again
        $('#loginForm, #signup-view, hr.my-4').show();

        // Reset modal title
        $('#authModalLabel').text('Login or Create an Account');

        // Clear any reset request alerts
        $('#reset-request-alert').hide().text('');

        // Reset all forms inside the modal
        $('#signupForm, #loginForm, #resetPasswordRequestForm').trigger('reset');
    });
});
