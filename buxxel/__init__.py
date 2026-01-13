from flask import Flask
from config import Config
from buxxel.buxxel import database  # supabase clients live here


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Check for essential configuration
    required_keys = [
        'SUPABASE_URL',
        'SUPABASE_SERVICE_KEY',
        'SUPABASE_ANON_KEY',
        'UPLOADCARE_PUBLIC_KEY',
        'UPLOADCARE_SECRET_KEY',
        'SECRET_KEY'
    ]
    missing = [k for k in required_keys if not app.config.get(k)]
    if missing:
        raise RuntimeError(f"Missing required config keys: {', '.join(missing)}")

    # Register blueprints
    from buxxel.routes import all_page_blueprints
    from .APIs.listings import listings_api_bp
    from .APIs.profiles import profiles_api_bp
    from .APIs.admin_orders import admin_orders_api_bp
    from .APIs.orders import orders_api_bp
    from .APIs.admin_api import admin_api_bp

    # register all page blueprints
    for bp in all_page_blueprints:
        app.register_blueprint(bp)
    app.register_blueprint(listings_api_bp)
    app.register_blueprint(profiles_api_bp)
    app.register_blueprint(admin_api_bp)
    app.register_blueprint(admin_orders_api_bp)
    app.register_blueprint(orders_api_bp)

    # Register context processors
    @app.context_processor
    def inject_global_vars():
        return dict(
            uploadcare_public_key=app.config['UPLOADCARE_PUBLIC_KEY'],
            supabase_url=app.config['SUPABASE_URL'],
            supabase_key=app.config['SUPABASE_ANON_KEY']
        )

    return app
