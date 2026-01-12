$(document).ready(function() {
    $('#loginForm').on('submit', async function(event) {
        event.preventDefault();

        const submitBtn = $(this).find('button[type="submit"]');
        const originalBtnHtml = submitBtn.html();
        const alertDiv = $('#login-alert');

        const email = $('#loginIdentifier').val();
        const password = $('#loginPassword').val();

        submitBtn.prop('disabled', true).html(
            '<span class="spinner-border spinner-border-sm" role="status"></span> Logging In...'
        );

        try {
            const { data, error } = await window.supabaseClient.auth.signInWithPassword({ email, password });
            if (error) {
                alertDiv.text(error.message).removeClass('alert-success').addClass('alert-danger').show();
                submitBtn.prop('disabled', false).html(originalBtnHtml);
            } else {
                location.reload();
            }
        } catch (err) {
            console.error("Unexpected login error:", err);
            alert("Login failed. Please try again.");
            submitBtn.prop('disabled', false).html(originalBtnHtml);
        }
    });
});
