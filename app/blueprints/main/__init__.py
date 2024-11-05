from flask import Blueprint

main_bp = Blueprint('main', __name__)

# Import the routes
from . import routes