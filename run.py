from buxxel import create_app

app = create_app()
 
# The development server is for local development only.
# In production, a WSGI server like Gunicorn or Waitress should be used.
# Example with Gunicorn: gunicorn --bind 0.0.0.0:8000 "run:app"
# Example with Waitress: waitress-serve --host 127.0.0.1 --port 8000 run:app
if __name__ == '__main__':
    app.run(debug=True)
