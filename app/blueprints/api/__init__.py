from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Import the routes
from . import routes