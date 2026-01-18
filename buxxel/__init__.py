# buxxel/__init__.py
import os
from flask import Flask
from buxxel.config import DevelopmentConfig, ProductionConfig
from buxxel import database  # supabase clients live here

# set configuration class
# change it to switch between dev and prod


def create_app(config = DevelopmentConfig):
    """Application factory with explicit configuration classes."""
    app = Flask(__name__, instance_relative_config=True)

    # Apply the chosen configuration class
    app.config.from_object(config)

    # Check for essential configuration keys
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
    from .routes import __all_api__
    from .routes import __all_views__

    for bp in __all_views__:
        app.register_blueprint(bp)

    for bp in __all_api__:
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
