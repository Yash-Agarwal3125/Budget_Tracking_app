from flask import Blueprint, render_template, abort
from database import get_db_connection
from datetime import datetime

# A Blueprint is a way to organize a group of related views and other code.
# Instead of registering views and other code directly with an application,
# they are registered with a blueprint.
views_bp = Blueprint('views', __name__)

# Route for the index page (main login/signup page)
@views_bp.route("/")
def index():
    """Renders the main index page."""
    return render_template("index.html")

# Route for the dashboard page
@views_bp.route("/dashboard")
def dashboard():
    """Renders the user dashboard."""
    return render_template("dashboard.html")

@views_bp.route("/reset-password/<token>")
def reset_password_page(token):
    """Renders the password reset page if the token is valid."""
    conn = get_db_connection()
    if not conn:
        abort(500, "Database connection failed")
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Check if token is valid and not expired
        query = "SELECT * FROM password_reset_tokens WHERE token = %s AND expires_at > %s"
        cursor.execute(query, (token, datetime.utcnow()))
        token_data = cursor.fetchone()

        if not token_data:
            # You can render a more user-friendly "invalid token" page here
            abort(404, "Invalid or expired password reset token.")
        
        return render_template("reset_password.html", token=token)
    finally:
        cursor.close()
        conn.close()
