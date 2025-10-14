from flask import Blueprint, render_template

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
