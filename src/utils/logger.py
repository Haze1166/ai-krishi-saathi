# Optional: Setup centralized logging configuration
import logging
import sys

def setup_logging(log_level=logging.INFO):
    """Configures basic logging."""
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    root_logger = logging.getLogger() # Get root logger
    root_logger.setLevel(log_level)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    # Optional: File Handler
    # file_handler = logging.FileHandler("krishi_saathi.log")
    # file_handler.setFormatter(log_formatter)
    # root_logger.addHandler(file_handler)

    logging.getLogger("werkzeug").setLevel(logging.WARNING) # Quieten Flask's default server logs if needed
    logging.getLogger("requests").setLevel(logging.WARNING) # Quieten requests library logs
    logging.getLogger("urllib3").setLevel(logging.WARNING) # Quieten underlying urllib logs

    root_logger.info("Logging configured.")

# Note: If using Flask's app.logger, Flask handles some setup.
# This function can be used for more custom configuration or logging outside Flask context.
# Call setup_logging() early in your app's lifecycle, e.g., in create_app() in app.py before returning app
# or just rely on Flask's default logger which is accessible via current_app.logger within requests.    