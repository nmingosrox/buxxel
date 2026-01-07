from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig
from .extensions import db, login_manager, migrate
from dotenv import load_dotenv
import os

load_dotenv()

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__, instance_relative_config=True)
   
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "users_bp.login_user"

    if not all([
      app.config.get('UPLOADCARE_PUBLIC_KEY'),
      app.config.get('UPLOADCARE_SECRET_KEY'),
      app.config.get('SECRET_KEY'),
      app.config.get('SQLALCHEMY_DATABASE_URI')  # or your DB connection string
    ]):
        raise RuntimeError("Missing one or more required configuration keys")
   
    # Register blueprints
    from .routes.main import main_bp
    from .APIs.listings import listings_bp
    from .APIs.users import users_bp
    from .routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(listings_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(users_bp)
    
    # Register context processors
    @app.context_processor
    def inject_global_vars():
        """Injects global variables into all templates."""
        return dict(
            uploadcare_public_key=app.config['UPLOADCARE_PUBLIC_KEY'],
        )

    return app
