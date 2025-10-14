# imports
from flask import Flask
from flask_cors import CORS

# Import blueprints from the route files
from views import views_bp
from auth import auth_bp
from transactions import transactions_bp

def create_app():
    """
    Application factory function to create and configure the Flask app.
    """
    # Initialize Flask app
    app = Flask(__name__)
    CORS(app)

    # Register the blueprints
    # These blueprints contain the routes from the other files
    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(transactions_bp, url_prefix='/api')

    return app

# The main entry point for the application
if __name__ == '__main__':
    app = create_app()
    # The debug flag is set to True for development purposes
    app.run(debug=True)
