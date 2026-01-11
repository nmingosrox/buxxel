# Generic WSGI entry point for Flask (or other WSGI apps)
import sys
import os

# Add your project directory to the Python path
# Example (PythonAnywhere): '/home/your_username/buxxelmod'
# On other servers, set this to the absolute path of your project root.
project_home = os.path.abspath(os.path.dirname(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the Flask application factory
from buxxel import create_app

# Create the WSGI application object
# WSGI servers (Gunicorn, uWSGI, Waitress, mod_wsgi, PythonAnywhere, etc.)
# will look for this 'application' object.
application = create_app()
