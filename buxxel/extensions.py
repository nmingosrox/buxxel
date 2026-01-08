# buxxel/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_admin import Admin

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
admin = Admin()

# Required: tell Flask-Login how to load a user from ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
