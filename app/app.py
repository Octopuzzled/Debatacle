from flask import Flask
from flask_session import Session
from logging.handlers import RotatingFileHandler
import logging

# Import blueprints
from blueprints.admin.routes import admin_bp
from blueprints.lessons.routes import lessons_bp
from blueprints.slides.routes import slides_bp
from blueprints.api.routes import api_bp
from blueprints.auth.routes import auth_bp

# Configure application
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
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(lessons_bp, url_prefix='/lessons')
app.register_blueprint(slides_bp, url_prefix='/slides')
app.register_blueprint(api_bp, url_prefix='/api')

# Run the flask app
if __name__ == "__main__":
    app.run(debug=True)