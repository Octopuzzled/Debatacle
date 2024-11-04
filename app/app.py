from flask import Flask
from flask_session import Session
from logging.handlers import RotatingFileHandler
import logging

# Import blueprints
from app.blueprints.admin.routes import admin_bp
from app.blueprints.lessons.routes import lessons_bp
from app.blueprints.slides.routes import slides_bp
from app.blueprints.api.routes import api_bp
from app.blueprints.auth.routes import auth_bp
from app.blueprints.dashboard import dashboard_bp

def create_app():
    app = Flask(__name__)

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
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(lessons_bp, url_prefix='/lessons')
    app.register_blueprint(slides_bp, url_prefix='/slides')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    return app

# Run the flask app
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)