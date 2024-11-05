from flask import Blueprint
from .utils import login_required, is_admin

auth_bp = Blueprint('auth', __name__)

__all__ = ['login_required', 'is_admin']

# Import the routes
from . import routes