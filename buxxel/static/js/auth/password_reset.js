$(document).ready(function() {
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

        try {
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
        } finally {
            submitBtn.prop('disabled', false).html(originalBtnHtml);
        }
    });
});
