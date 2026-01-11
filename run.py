from buxxel import create_app

app = create_app()

# The development server below is for local development only.
# On PythonAnywhere, you should NOT run the app with app.run().
# Instead, configure your WSGI file (usually located at /var/www/<your-username>_pythonanywhere_com_wsgi.py)
# to import this app object:
#
#     from run import app
#
# PythonAnywhere will then serve your app using its own WSGI servers.
#
# For local testing:
if __name__ == '__main__':
    app.run(debug=True)
