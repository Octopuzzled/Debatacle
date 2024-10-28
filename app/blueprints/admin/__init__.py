from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

# Import routes to register with the blueprint
from .routes import *