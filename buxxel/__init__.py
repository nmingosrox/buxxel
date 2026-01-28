# buxxel/__init__.py
import os
from flask import Flask
from buxxel.config import DevelopmentConfig, ProductionConfig
from buxxel import database  # supabase clients live here
from jinja2 import TemplateNotFound

# set configuration class
# change it to switch between dev and prod


def create_app(config = DevelopmentConfig):
    """Application factory with explicit configuration classes."""
    app = Flask(__name__, instance_relative_config=True)

    # Apply the chosen configuration class
    app.config.from_object(config)

    # Check for essential configuration keys
    required_keys = [
        'SB_URL',
        'SB_SECRET_KEY',
        'SB_PUBLISHABLE_KEY',
        'UC_PUBLIC_KEY',
        'UC_SECRET_KEY',
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

    # Global error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("error_pages/e_404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("error_pages/e_500.html"), 500

    # Register context processors
    @app.context_processor
    def inject_global_vars():
        return dict(
            uploadcare_public_key=app.config['UC_PUBLIC_KEY'],
            supabase_url=app.config['SB_URL'],
            supabase_key=app.config['SB_PUBLISHABLE_KEY']
        )

    return app
