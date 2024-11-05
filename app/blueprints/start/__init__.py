from flask import Blueprint

start_bp = Blueprint('start', __name__)

# Import the routes
from . import routes