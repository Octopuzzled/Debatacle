from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Import routes to register with the blueprint
from .routes import *