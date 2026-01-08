from flask_login import current_user

@main_bp.route("/test")
def test():
    return f"Authenticated? {current_user.is_authenticated}"
