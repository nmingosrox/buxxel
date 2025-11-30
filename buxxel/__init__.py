from flask import Flask
from config import Config
from buxxel import extensions

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Check for essential configuration
    if not all([app.config['SUPABASE_URL'], app.config['SUPABASE_SERVICE_KEY'], app.config['SUPABASE_ANON_KEY'], app.config['UPLOADCARE_PUBLIC_KEY'], app.config.get('SECRET_KEY')]):
        raise ValueError("All required credentials (SECRET_KEY, Supabase, Uploadcare) must be set in the environment or config.")

    # Initialize extensions
    # The standard client is for public or user-specific operations. It starts with the anon key
    # and will be "upgraded" with a user's JWT for authenticated requests.
    extensions.supabase = extensions.create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_ANON_KEY'])
    # The admin client uses the service role key for admin tasks and bypasses RLS.
    extensions.supabase_admin = extensions.create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_SERVICE_KEY'])

    # Register blueprints
    from .routes.main import main_bp
    from .routes.dashboard import dashboard_bp
    from .APIs.listings import listings_api_bp
    from .APIs.profiles import profiles_api_bp
    from .routes.checkout import checkout_bp
    from .routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(listings_api_bp)
    app.register_blueprint(profiles_api_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(admin_bp)

    # Register context processors
    @app.context_processor
    def inject_global_vars():
        """Injects global variables into all templates."""
        return dict(
            uploadcare_public_key=app.config['UPLOADCARE_PUBLIC_KEY'],
            supabase_url=app.config['SUPABASE_URL'],
            supabase_key=app.config['SUPABASE_ANON_KEY'] # Pass the public ANON key to the frontend
        )

    return app
