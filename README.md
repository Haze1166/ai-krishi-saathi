# AI Krishi Saathi - Voice-Driven AI Assistant for Farmers

**Vision:** Empower small and marginal farmers with accessible, voice-based AI assistance for better farming outcomes, financial access, and market linkage using basic phones in local languages.

## Project Overview

This repository contains the backend source code for AI Krishi Saathi, implemented using Python and Flask. It provides API endpoints designed to integrate with IVR/Telephony systems (like Twilio, Exotel) and WhatsApp Business API to deliver:

*   Voice-Based Crop Advisory
*   Voice Q&A System
*   AI-Powered Crop Disease Detection (via Image/Symptoms)
*   Localized Weather Forecasts
*   Smart Crop Financing Information (Eligibility Simulation)
*   Market Price Information & Forecasts (Simulation)
*   Market Linkage Assistance (Simulation)

**Status:** This code provides a functional structure with **simulated** core logic and placeholder integrations. Significant development is required to replace simulations with real AI models and external API calls.

## Technology Stack

*   **Backend:** Python 3.x, Flask
*   **Configuration:** python-dotenv
*   **API Interaction:** requests
*   **Placeholders/Integration Points for:**
    *   **Voice/Telephony:** Twilio, Exotel (Requires specific libraries and webhook handling)
    *   **WhatsApp:** Twilio WhatsApp API, Gupshup, etc.
    *   **NLP/NLU:** Google Dialogflow / Cloud AI, Azure LUIS / Bot Service, Rasa, Bhashini (Requires SDKs/APIs)
    *   **STT/TTS:** Cloud Services (Google, Azure, AWS), Bhashini (Requires SDKs/APIs)
    *   **AI/ML Models:**
        *   Disease Detection: TensorFlow/Keras/PyTorch (Requires training, saved models)
        *   Price Forecasting: Time Series Models (e.g., ARIMA, Prophet, LSTM) (Requires training, saved models)
        *   Advisory Engine: Rules-based, potentially ML-enhanced
    *   **Databases:** PostgreSQL/MySQL recommended (Requires ORM like SQLAlchemy, DB driver) - Currently uses an in-memory dict placeholder.
    *   **External APIs:** Weather (OpenWeatherMap example), Market Data (Agmarknet, eNAM - finding APIs can be hard), Financial Schemes (PMFBY, KCC - usually requires scraping or specific partnerships).
*   **Deployment:** Docker, Gunicorn/Waitress, Cloud Platform (AWS, GCP, Azure)

## Repository Structure