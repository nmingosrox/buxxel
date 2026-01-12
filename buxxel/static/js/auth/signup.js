$(document).ready(function() {
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
            '<span class="spinner-border spinner-border-sm" role="status"></span> Signing Up...'
        );

        try {
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
                    form.trigger('reset');
                    alertDiv.hide().text('');
                }, 4000);
            }
        } finally {
            submitBtn.prop('disabled', false).html(originalBtnHtml);
        }
    });
});
