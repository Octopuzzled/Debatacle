from flask import Blueprint

# Create the dashboard blueprint
dashboard_bp = Blueprint('dashboard', __name__)

from .routes import *  # Import routes after initializing the blueprint
