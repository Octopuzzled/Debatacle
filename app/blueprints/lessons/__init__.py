from flask import Blueprint

lessons_bp = Blueprint('lessons', __name__)

# Import routes to register with the blueprint
from .routes import *