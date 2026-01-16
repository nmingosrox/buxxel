# buxxel/__init__.py
import os
from flask import Flask
from buxxel.config import DevelopmentConfig, ProductionConfig
from buxxel import database  # supabase clients live here


def create_app(config_name="development"):
    """Application factory with explicit configuration classes."""
    app = Flask(__name__, instance_relative_config=True)

    # Explicitly choose config class
    if config_name == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

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
    from .routes import __all__ as all_pages
    from .routes.apis import __all__ as all_apis

    for bp in all_pages:
        app.register_blueprint(bp)

    for bp in all_apis:
        app.register_blueprint(bp)

    # Register context processors
    @app.context_processor
    def inject_global_vars():
        return dict(
            uploadcare_public_key=app.config['UPLOADCARE_PUBLIC_KEY'],
            supabase_url=app.config['SUPABASE_URL'],
            supabase_key=app.config['SUPABASE_ANON_KEY']
        )

    return app
