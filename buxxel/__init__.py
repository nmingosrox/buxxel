from flask import Flask
from buxxel.config import Config
from buxxel import database  # supabase clients live here


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
    # The blueprints are exposed by __init__.py files inside modules
    # Register blueprints
    from .routes import __all__ as all_pages
    from .APIs import __all__ as all_apis
    
    # register all page blueprints
    for bp in all_pages:
        app.register_blueprint(bp)
        
    # register all API blueprints
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
