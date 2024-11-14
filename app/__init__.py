from flask import Flask
from flask_session import Session
from logging.handlers import RotatingFileHandler
import logging
from dotenv import load_dotenv
import os

# Import blueprints - Blueprints where suggested by ChatGPT after I asked how to refactor my very long app.py
from app.blueprints.main.routes import main_bp
from app.blueprints.start.routes import start_bp
from app.blueprints.admin.routes import admin_bp
from app.blueprints.lessons.routes import lessons_bp
from app.blueprints.slides.routes import slides_bp
from app.blueprints.api.routes import api_bp
from app.blueprints.auth.routes import auth_bp
from app.blueprints.dashboard.routes import dashboard_bp
from app.blueprints.quiz.routes import quiz_bp

def create_app():
    load_dotenv
    app = Flask(__name__)

    app.secret_key = os.environ.get('SECRET_KEY')
    
    # Configure logging for debugging
    handler = RotatingFileHandler('app.log', maxBytes=5 * 1024 * 1024, backupCount=5)  # 5 MB per file, keep 5 backups
    handler.setLevel(logging.ERROR)  # Set the logging level
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the root logger
    logging.getLogger().addHandler(handler)

    # Set the logging level for the root logger
    logging.getLogger().setLevel(logging.ERROR)  # Error should be sufficient for now

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(start_bp, url_prefix='/start')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(lessons_bp, url_prefix='/lessons')
    app.register_blueprint(slides_bp, url_prefix='/slides')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(quiz_bp, url_prefix='/api/quiz')

    return app