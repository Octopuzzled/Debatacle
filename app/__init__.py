from flask import Flask
from .blueprints.auth import auth_bp
from .blueprints.admin import admin_bp
from .blueprints.lessons import lessons_bp
from .blueprints.slides import slides_bp

def create_app():
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(lessons_bp, url_prefix='/lessons')
    app.register_blueprint(slides_bp, url_prefix='/slides')
    
    return app