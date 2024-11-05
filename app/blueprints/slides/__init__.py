from flask import Blueprint

slides_bp = Blueprint('slides', __name__)

# Import routes to register with the blueprint
from . import routes