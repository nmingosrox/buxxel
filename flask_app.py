# flask_app.py
import sys
import os
from buxxel import ProductionConfig

# Absolute path to your project root
project_home = os.path.abspath(os.path.dirname(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the Flask application factory
try:
    from buxxel import create_app
except ImportError as e:
    raise RuntimeError("Failed to import create_app from buxxel")
# Create the WSGI application object
# WSGI servers (Gunicorn, uWSGI, Waitress, mod_wsgi, PythonAnywhere, etc.)
# will look for this 'application' object.
app = create_app(config = ProductionConfig)
