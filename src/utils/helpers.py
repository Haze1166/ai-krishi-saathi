# Optional: Add common utility functions here
import requests
from flask import current_app

def download_audio(url):
    """Downloads audio content from a URL. Add authentication if needed."""
    logger = current_app.logger
    try:
        # Add authentication headers/params if required by your IVR provider
        # e.g., auth=(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN) for Twilio
        response = requests.get(url, stream=True, timeout=15) # 15 second timeout
        response.raise_for_status()
        logger.info(f"Successfully downloaded audio from {url}")
        return response.content # Return audio bytes
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download audio from {url}: {e}")
        return None

# Add other helpers like location to lat/lon conversion, etc.
# def get_lat_lon_for_location(location_name): ...