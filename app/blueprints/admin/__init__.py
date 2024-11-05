from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

# Import the routes
from . import routes