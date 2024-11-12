from flask import Blueprint

quiz_bp = Blueprint('quiz', __name__)

# Import the routes
from . import routes