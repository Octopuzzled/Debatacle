from flask import Blueprint

lessons_bp = Blueprint('lessons', __name__)

# Import the routes
from . import routes