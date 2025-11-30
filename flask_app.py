# THIS FILE IS FOR CONFIGURING PYTHONANYWHERE MY HOSTING SERVICE
import sys
import os

# Add the project directory to the Python path
# Replace 'your_username' with your actual PythonAnywhere username.
# This assumes 'buxxelmod' is the root directory of your project
# and 'flask_app.py' is directly inside it.
project_home = u'/home/your_username/buxxelmod'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the create_app function from your application package
from buxxel import create_app

# Create the Flask application instance
application = create_app()