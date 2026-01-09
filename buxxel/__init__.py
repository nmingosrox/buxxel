from flask import Flask
from config import DevelopmentConfig
from .extensions import db, login_manager, migrate, admin
from dotenv import load_dotenv
import os
from buxxel.models import User, Listing
from buxxel.admin_views import UserAdmin, ListingAdminView

load_dotenv()

# Required: tell Flask-Login how to load a user from ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__, instance_relative_config=True)
   
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app)
   
    # Login view
    login_manager.login_view = "users_bp.login"

    # Ensure required config keys exist
    if not all([
      app.config.get('UPLOADCARE_PUBLIC_KEY'),
      app.config.get('UPLOADCARE_SECRET_KEY'),
      app.config.get('SECRET_KEY'),
      app.config.get('SQLALCHEMY_DATABASE_URI')
    ]):
        raise RuntimeError("Missing one or more required configuration keys")
   
    # Register blueprints
    from .routes.main import main_bp
    from .APIs.users import users_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp)
   
    # Admin views
    admin.add_view(ListingAdminView(Listing, db.session))  # ✅ one view for all listings
    admin.add_view(UserAdmin(User, db.session))            # ✅ user management

    # Register context processors
    @app.context_processor
    def inject_global_vars():
        """Injects global variables into all templates."""
        return dict(
            uploadcare_public_key=app.config['UPLOADCARE_PUBLIC_KEY'],
        )

    return app
