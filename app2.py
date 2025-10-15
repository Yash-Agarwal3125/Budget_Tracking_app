# imports
from flask import Flask
from flask_cors import CORS
from flask_mail import Mail, Message # Import Mail and Message
import os # Import os to handle environment variables

# Import blueprints from the route files
from views import views_bp
from auth import auth_bp
from extention import mail
from transactions import transactions_bp

# Global mail instance
mail = Mail()

def create_app():
    """
    Application factory function to create and configure the Flask app.
    """
    # Initialize Flask app
    app = Flask(__name__)
    CORS(app)

    # --- ADD MAIL CONFIGURATION ---
    # IMPORTANT: Use environment variables in production for security
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'yash.agarwal2023a@vitstudent.ac.in') # Your email address
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'eqbi jcuy ikxj exwy') # Your email app password
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

    # Initialize the mail extension
    mail.init_app(app)

    # Register the blueprints
    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(transactions_bp, url_prefix='/api')

    return app

# The main entry point for the application
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0',debug=True)