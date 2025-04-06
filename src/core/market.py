import random
import datetime
from flask import current_app
# Optional: Import API calling functions if defined separately
# from src.integrations.external_apis import get_agmarknet_prices_api

def get_market_prices(crop, location):
    """
    Placeholder: Fetches current market prices for a crop near a location.
    !! REPLACE with actual API calls to Agmarknet, eNAM, or other market data providers !!
    """
    logger = current_app.logger
    logger.info(f"[SIMULATE] Market: Fetching prices for {crop} near {location}")

    prices_text = "अभी मंडी भाव उपलब्ध नहीं हैं।"
    simulated_prices = []

    # --- Simulation Logic ---
    # Assume location gives us nearby mandis. A real system needs a location-to-mandi mapping.
    mandis = ["कानपुर मंडी", "लखनऊ मंडी", "झाँसी मंडी", "बांदा मंडी"] # Example mandis for Bundelkhand/UP
    relevant_mandis = random.sample(mandis, k=random.randint(1, 3))

    # Simulate base price based on crop
    base_price = {"गेहूं": 2100, "बाजरा": 1900, "धान": 1850, "चना": 4500}.get(crop, 2000)
    price_variation = int(base_price * 0.1) # +/- 10% variation

    for mandi in relevant_mandis:
        price = base_price + random.randint(-price_variation, price_variation)
        # Ensure price is reasonable
        price = max(500, price)
        simulated_prices.append({"mandi_name": mandi, "price_per_quintal": price})

    if simulated_prices:
        price_strings = [f"{p['mandi_name']} में ~₹{p['price_per_quintal']}/क्विंटल" for p in simulated_prices]
        prices_text = f"{crop} का वर्तमान भाव: " + ", ".join(price_strings) + "."

    result = {"prices_text": prices_text, "price_data": simulated_prices}
    logger.info(f"[SIMULATE] Market Prices Result: {result}")
    return result


def get_price_forecast(crop, location, days_ahead=7):
    """
    Placeholder: Predicts future market prices.
    !! REPLACE with a trained time-series forecasting model or detailed analysis !!
    """
    logger = current_app.logger
    logger.info(f"[SIMULATE] Market: Forecasting prices for {crop} near {location} ({days_ahead} days)")

    forecast_text = "मूल्य पूर्वानुमान अभी उपलब्ध नहीं है।"

    # --- Simulation Logic ---
    # Requires a trained model (e.g., ARIMA, Prophet, LSTM) using historical price, weather, demand data.
    # Or complex rule-based analysis.

    # Simple simulation based on random trend:
    try:
        # Use current price simulation as base
        current_price_result = get_market_prices(crop, location)
        if current_price_result["price_data"]:
             base_price = current_price_result["price_data"][0]["price_per_quintal"] # Use first mandi price
        else:
             base_price = {"गेहूं": 2100, "बाजरा": 1900, "धान": 1850, "चना": 4500}.get(crop, 2000) # Fallback base

        trend = random.choice([-0.03, -0.01, 0, 0.01, 0.04]) # Simulate % change per week
        predicted_price = int(base_price * (1 + (trend * (days_ahead / 7.0))))
        predicted_price = max(500, predicted_price) # Ensure reasonable price

        if trend > 0.005:
            forecast_text = f"पूर्वानुमान: अगले {days_ahead} दिनों में भाव थोड़ा बढ़कर ₹{predicted_price}/क्विंटल के आसपास जा सकता है।"
        elif trend < -0.005:
            forecast_text = f"पूर्वानुमान: अगले {days_ahead} दिनों में भाव थोड़ा गिरकर ₹{predicted_price}/क्विंटल के आसपास रह सकता है।"
        else:
            forecast_text = f"पूर्वानुमान: अगले {days_ahead} दिनों में भाव लगभग स्थिर (₹{predicted_price}/क्विंटल) रहने की संभावना है।"

    except Exception as e:
        logger.error(f"Error during simulated price forecast: {e}")
        forecast_text = "मूल्य पूर्वानुमान गणना में त्रुटि हुई।"


    result = {"forecast_text": forecast_text}
    logger.info(f"[SIMULATE] Price Forecast Result: {result}")
    return result


def find_buyers(crop, location, quantity):
    """
    Placeholder: Finds potential buyers (FPOs, traders) near the farmer.
    !! REPLACE with database query or API call to a buyer platform !!
    """
    logger = current_app.logger
    logger.info(f"[SIMULATE] Market Linkage: Finding buyers for {quantity} quintals of {crop} near {location}")

    message = "अभी आपके क्षेत्र में खरीदार की जानकारी उपलब्ध नहीं है।"
    buyer_name = None
    buyer_contact = None

    # --- Simulation Logic ---
    # Needs a database of registered buyers with location, crops handled, contact info.
    buyers_db = [
        {"name": "प्रगति किसान उत्पादक संगठन (FPO)", "contact": "98xxxxxx01", "type": "FPO", "location": "Nearby"},
        {"name": "अग्रवाल अनाज भंडार", "contact": "99xxxxxx02", "type": "Local Trader", "location": "Nearby"},
        {"name": "सरकारी खरीद केंद्र (MSPC)", "contact": "स्थानीय केंद्र पर संपर्क करें", "type": "Government", "location": "Nearby"},
        {"name": "विकास फूड प्रोसेसिंग यूनिट", "contact": "97xxxxxx03", "type": "Processor", "location": "District"},
    ]

    potential_buyers = buyers_db # Simple simulation - assume all are potential
    if potential_buyers:
        found_buyer = random.choice(potential_buyers)
        buyer_name = found_buyer["name"]
        buyer_contact = found_buyer["contact"]
        message = f"{quantity} क्विंटल {crop} के लिए एक संभावित खरीदार: {buyer_name} ({found_buyer['type']})।"
        if buyer_contact and "संपर्क करें" not in buyer_contact:
             message += f" संपर्क विवरण SMS द्वारा भेजा जाएगा।"
             # Note: Actual SMS sending happens in the API route after calling this function.
        else:
            message += f" आप सीधे {buyer_contact}।"


    result = {"message": message, "name": buyer_name, "contact": buyer_contact}
    logger.info(f"[SIMULATE] Buyer Linkage Result: {result}")
    return result