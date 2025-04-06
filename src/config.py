import os
from dotenv import load_dotenv

# Load environment variables from a .env file in the project root
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print("Warning: .env file not found. Relying on system environment variables.")

class Config:
    """Application configuration variables."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key-CHANGE-IN-PRODUCTION')

    # --- External Service API Keys ---
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER') # Your Twilio number for IVR/SMS

    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') # For Dialogflow/Google Cloud AI
    BHASHINI_API_KEY = os.environ.get('BHASHINI_API_KEY') # Placeholder for Bhashini
    BHASHINI_API_ENDPOINT = os.environ.get('BHASHINI_API_ENDPOINT') # Placeholder

    OPENWEATHERMAP_API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY') # Example weather API

    AGMARKNET_API_KEY = os.environ.get('AGMARKNET_API_KEY') # Placeholder for market data API
    AGMARKNET_API_ENDPOINT = os.environ.get('AGMARKNET_API_ENDPOINT') # Placeholder

    # --- Model Paths ---
    # Ensure paths are relative to the project root or absolute
    DISEASE_MODEL_PATH = os.environ.get('DISEASE_MODEL_PATH', os.path.join(os.path.dirname(__file__), 'models', 'disease_model.pkl'))
    PRICE_MODEL_PATH = os.environ.get('PRICE_MODEL_PATH', os.path.join(os.path.dirname(__file__), 'models', 'price_forecast_model.joblib'))

    # --- Database ---
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///./krishi_saathi.db') # Default to SQLite in project root

    # --- Other Settings ---
    DEFAULT_LANGUAGE = os.environ.get('DEFAULT_LANGUAGE', 'hi-IN') # Hindi-India
    SUPPORTED_LANGUAGES = os.environ.get('SUPPORTED_LANGUAGES', 'hi-IN,en-IN,mr-IN').split(',')

# Create a config object for easy import
config = Config()

# Print a warning if essential keys are missing (optional but helpful)
if not config.TWILIO_ACCOUNT_SID or not config.TWILIO_AUTH_TOKEN:
    print("Warning: Twilio credentials not found in environment variables.")
# Add similar checks for other critical keys