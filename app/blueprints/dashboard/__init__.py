from flask import Blueprint

# Create the dashboard blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# Import the routes
from . import routes
