from flask import Flask
from src.api.routes import api_bp
from src.config import config
# Optional: Import database setup if using SQLAlchemy or similar
# from src.database import db # Example
# Optional: Import and configure logging
# from src.utils.logger import setup_logging

def create_app():
    """Creates and configures the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config)

    # Optional: Initialize extensions like database
    # db.init_app(app)

    # Optional: Setup logging
    # setup_logging() # Make sure logger is configured

    # Register blueprints (API routes)
    app.register_blueprint(api_bp, url_prefix='/api') # All API routes will be under /api

    # Basic root endpoint for health check or info
    @app.route('/')
    def index():
        return "Welcome to AI Krishi Saathi Backend! API endpoints are under /api"

    # Example: Log loaded configuration (be careful not to log secrets)
    app.logger.info("Flask app created.")
    app.logger.info(f"Default Language: {app.config.get('DEFAULT_LANGUAGE')}")
    app.logger.info(f"Supported Languages: {app.config.get('SUPPORTED_LANGUAGES')}")
    # Use app.logger for logging within Flask context after app creation

    return app

# This allows running the app directly using 'flask run' or 'python src/app.py'
if __name__ == '__main__':
    app = create_app()
    # Use Gunicorn or Waitress for production instead of app.run()
    app.run(host='0.0.0.0', port=5000, debug=True) # Debug=True only for development!