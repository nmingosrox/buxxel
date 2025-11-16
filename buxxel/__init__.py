from flask import Flask
from config import Config
from buxxel import extensions

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Check for essential configuration
    if not all([app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'], app.config['UPLOADCARE_PUBLIC_KEY']]):
        raise ValueError("Supabase and Uploadcare credentials must be set in the environment or config.")

    # Initialize extensions
    extensions.supabase = extensions.create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'])

    # Register blueprints
    from .routes.main import main_bp
    from .routes.dashboard import dashboard_bp
    from .routes.admin import admin_bp
    from .APIs.listings import listings_api_bp
    from .APIs.profiles import profiles_api_bp
    from .APIs.admin import admin_api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(listings_api_bp)
    app.register_blueprint(profiles_api_bp)
    app.register_blueprint(admin_api_bp)

    # Register context processors
    @app.context_processor
    def inject_uploadcare_key():
        """Injects the Uploadcare public key into all templates."""
        return dict(uploadcare_public_key=app.config['UPLOADCARE_PUBLIC_KEY'])


    return app
