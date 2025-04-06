from flask import Blueprint, request, jsonify, current_app
import datetime
import requests # Needed for fetching media in WhatsApp simulation
from src.config import config # Use Flask's current_app.config instead? Usually better.
from src.core import language, advisory, disease_detection, finance, market, weather
from src.integrations import telephony

api_bp = Blueprint('api', __name__)

# --- !! TEMPORARY IN-MEMORY DATABASE FOR CONTEXT !! ---
# --- !! REPLACE THIS WITH A REAL DATABASE (PostgreSQL/MySQL) !! ---
farmer_context_db = {}
# Example structure:
# farmer_context_db = {
#    "+15551234567": { "id": "+15551234567", "language": "hi-IN", "location": "Bundelkhand", ... },
#    "whatsapp:+15559876543": { "id": "whatsapp:+15559876543", "language": "en-IN", ... }
# }

def get_farmer_context(caller_id):
    """Retrieves or creates context for a farmer."""
    # Use Flask logger
    logger = current_app.logger
    if caller_id not in farmer_context_db:
        logger.info(f"Creating new context for caller: {caller_id}")
        # Derive initial context (e.g., default language, maybe guess location later)
        farmer_context_db[caller_id] = {
            "id": caller_id,
            "language": config.DEFAULT_LANGUAGE, # Use config directly or app.config
            "location": "Unknown", # Should be derived (e.g., from area code) or asked
            "current_crop": "गेहूं", # Example default, should be dynamic or asked
            "land_size_acres": 2.0, # Example default
            "sowing_date": None, # Important for advisory! Needs to be set.
            "last_interaction_time": datetime.datetime.now(),
            "last_query": None,
        }
    else:
         # Update interaction time on access
         farmer_context_db[caller_id]["last_interaction_time"] = datetime.datetime.now()

    return farmer_context_db[caller_id]

def update_farmer_context(caller_id, updates):
    """Updates farmer context."""
    logger = current_app.logger
    if caller_id in farmer_context_db:
        logger.debug(f"Updating context for {caller_id}: {updates}")
        farmer_context_db[caller_id].update(updates)
    else:
        logger.warning(f"Attempted to update context for non-existent caller: {caller_id}")

# --- API Endpoints ---

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    return jsonify({"status": "ok", "timestamp": datetime.datetime.utcnow().isoformat()}), 200

@api_bp.route('/ivr/welcome', methods=['POST'])
def ivr_welcome():
    """
    Endpoint for IVR systems (Twilio/Exotel) when a farmer calls.
    Returns instructions for the IVR (e.g., TwiML or JSON).
    """
    logger = current_app.logger
    try:
        # --- Get Caller ID ---
        # Adjust based on your IVR provider's request format
        # For Twilio: request.form.get('From')
        # For Exotel: request.form.get('From')
        # Simulating from JSON body for testing:
        if request.is_json:
            caller_id = request.json.get('caller_id')
        else:
            # Try form data if not JSON
            caller_id = request.form.get('From', request.form.get('caller_id'))

        if not caller_id:
            logger.error("IVR Welcome: Missing caller_id in request.")
            return jsonify({"error": "Missing caller_id"}), 400

        logger.info(f"IVR Welcome call received from: {caller_id}")
        farmer_context = get_farmer_context(caller_id)
        lang = farmer_context.get('language', config.DEFAULT_LANGUAGE)

        # --- Prepare Welcome Message ---
        # TODO: Select message based on language (lang)
        welcome_message = "कृषि साथी में आपका स्वागत है। आप क्या जानना चाहते हैं? फसल सलाह, मंडी भाव, या कुछ और?"

        # --- Generate IVR Response ---
        # This needs to be formatted EXACTLY as your IVR provider expects.
        # Example Simulation (Generic JSON describing action):
        ivr_response = {
            "action": "SPEAK_AND_LISTEN", # Tell IVR to say something and wait for speech
            "payload": {
                "text_to_speak": welcome_message,
                "language": lang, # e.g., 'hi-IN', 'en-IN'
                 # URL on *this* server that the IVR should call back with the speech result
                "callback_url": request.host_url.rstrip('/') + '/api/ivr/handle-query',
                "speech_timeout": 5 # seconds to wait for speech
            }
        }
        # For Twilio, you'd generate TwiML instead using the twilio library:
        # from twilio.twiml.voice_response import VoiceResponse, Gather
        # response = VoiceResponse()
        # gather = Gather(input='speech', action='/api/ivr/handle-query', method='POST', language=lang, speechTimeout='auto')
        # gather.say(welcome_message, language=lang)
        # response.append(gather)
        # response.say("हमने आपकी प्रतिक्रिया प्राप्त नहीं की। बाद में पुन: प्रयास करें।", language=lang) # Fallback if no speech
        # return Response(str(response), mimetype='text/xml')

        logger.debug(f"IVR Welcome response for {caller_id}: {ivr_response}")
        return jsonify(ivr_response)

    except Exception as e:
        logger.exception(f"Error in /ivr/welcome: {e}")
        # Generic error response for IVR
        error_response = {
            "action": "SPEAK_AND_HANGUP",
            "payload": {"text_to_speak": "क्षमा करें, एक तकनीकी समस्या हुई है। कृपया बाद में कॉल करें।", "language": config.DEFAULT_LANGUAGE}
        }
        return jsonify(error_response), 500


@api_bp.route('/ivr/handle-query', methods=['POST'])
def handle_query():
    """
    Endpoint called by IVR after capturing farmer's speech input.
    Processes the query and returns the next IVR action.
    """
    logger = current_app.logger
    try:
        # --- Extract Data from IVR Callback ---
        # Adjust based on your provider's callback format
        # Twilio: caller_id = request.form.get('From'), speech_text = request.form.get('SpeechResult')
        # Exotel: caller_id = request.form.get('From'), speech_url = request.form.get('RecordingUrl')
        # Simulating from JSON body:
        if request.is_json:
            caller_id = request.json.get('caller_id')
            spoken_text = request.json.get('spoken_text') # Assume STT happened externally or passed for simulation
            audio_url = request.json.get('audio_url') # URL if STT needs to happen here
        else:
            # Try form data
            caller_id = request.form.get('From', request.form.get('caller_id'))
            spoken_text = request.form.get('SpeechResult', request.form.get('spoken_text'))
            audio_url = request.form.get('RecordingUrl', request.form.get('audio_url'))

        if not caller_id:
            logger.error("IVR Handle Query: Missing caller_id.")
            return jsonify({"error": "Missing caller_id"}), 400

        logger.info(f"IVR Query received from: {caller_id}")
        farmer_context = get_farmer_context(caller_id)
        lang = farmer_context.get('language', config.DEFAULT_LANGUAGE)

        # --- Perform Speech-to-Text (if needed) ---
        if not spoken_text and audio_url:
            logger.info(f"Performing STT for audio URL: {audio_url}")
            # !! REPLACE WITH ACTUAL STT CALL !!
            # audio_data = download_audio(audio_url) # Helper function needed
            spoken_text = language.speech_to_text(f"simulated_audio_from_{audio_url}", language_code=lang)
            logger.info(f"STT Result for {caller_id}: '{spoken_text}'")

        if not spoken_text:
            logger.warning(f"No speech input received or STT failed for {caller_id}.")
            response_text = "मुझे आपकी बात समझ नहीं आई। कृपया फिर से कहें।" # TODO: Localize
            ivr_response = {"action": "SPEAK_AND_LISTEN", "payload": {"text_to_speak": response_text, "language": lang, "callback_url": request.host_url.rstrip('/') + '/api/ivr/handle-query'}}
            return jsonify(ivr_response)

        update_farmer_context(caller_id, {"last_query": spoken_text})
        logger.info(f"Farmer {caller_id} asked: '{spoken_text}'")

        # --- Understand Intent and Entities ---
        # !! REPLACE WITH ACTUAL NLU CALL !!
        intent_data = language.understand_intent(spoken_text, language_code=lang)
        intent = intent_data.get("intent", "UNKNOWN")
        entities = intent_data.get("entities", {})
        logger.info(f"NLU Result for '{spoken_text}': Intent={intent}, Entities={entities}")

        # --- Get Context Variables ---
        # Try to get crop from entities, fallback to context, fallback to default
        crop = entities.get("crop", farmer_context.get("current_crop", "गेहूं"))
        # Ensure location is set, prompt if unknown (more advanced IVR flow needed)
        location = farmer_context.get("location", "Bundelkhand") # Default if unknown
        if location == "Unknown":
             logger.warning(f"Location unknown for farmer {caller_id}. Using default.")
             # TODO: Add logic to ask for location if unknown in a real system

        # --- Route to Core Logic Based on Intent ---
        response_text = "माफ़ कीजिए, मैं अभी इस बारे में सहायता नहीं कर सकता।" # Default response (TODO: Localize)

        try:
            if intent in ["CROP_ADVISORY_WATER", "CROP_ADVISORY_FERTILIZER", "CROP_ADVISORY_GENERAL"]:
                # Pass context which might contain sowing_date etc.
                advice_result = advisory.get_crop_advice(crop, location, farmer_context)
                response_text = advice_result.get("advice", response_text) # Expecting dict now
            elif intent == "DISEASE_QUERY_SYMPTOMS":
                symptom_text = entities.get("symptoms", spoken_text) # Extract specific symptoms if possible
                diagnosis_result = disease_detection.diagnose_from_symptoms(symptom_text, crop, location)
                response_text = diagnosis_result.get("diagnosis", response_text) + " " + diagnosis_result.get("advice", "")
                response_text += " सटीक निदान के लिए, आप व्हाट्सएप पर फसल की फोटो भेज सकते हैं।" # TODO: Localize
            elif intent == "FINANCE_LOAN_REQUEST":
                eligibility_result = finance.check_loan_eligibility(farmer_context) # Pass farmer data
                response_text = eligibility_result.get("message", response_text) # Expecting dict
            elif intent == "FINANCE_INSURANCE_QUERY":
                 insurance_info = finance.get_insurance_info(crop, location)
                 response_text = insurance_info.get("info", response_text)
            elif intent == "MARKET_PRICE_QUERY":
                prices_result = market.get_market_prices(crop, location)
                forecast_result = market.get_price_forecast(crop, location)
                response_text = prices_result.get("prices_text", "भाव उपलब्ध नहीं।") + " " + forecast_result.get("forecast_text", "")
            elif intent == "MARKET_LINKAGE_REQUEST":
                # Assume quantity from context or ask in a multi-turn convo
                quantity = farmer_context.get('typical_yield_quintals', 10) # Example default
                buyer_result = market.find_buyers(crop, location, quantity)
                response_text = buyer_result.get("message", response_text)
                if buyer_result.get("contact"):
                    # !! REPLACE WITH ACTUAL SMS SENDING !!
                    sms_text = f"कृषि साथी: {crop} खरीदार - {buyer_result.get('name')}, संपर्क: {buyer_result.get('contact')}"
                    telephony.send_sms(farmer_context['id'], sms_text) # Send contact via SMS
                    response_text += " खरीदार का संपर्क विवरण आपके मोबाइल पर SMS कर दिया गया है।" # TODO: Localize
            elif intent == "WEATHER_QUERY":
                 weather_info = weather.get_weather_forecast(location)
                 response_text = weather_info.get("forecast", response_text)
            elif intent == "GENERAL_QNA":
                query = entities.get("query_text", spoken_text)
                answer = advisory.get_general_qna_answer(query, crop, location)
                response_text = answer.get("answer", response_text)
            else: # Fallback / Unknown Intent
                logger.warning(f"Unhandled intent '{intent}' for query: '{spoken_text}'")
                response_text = "आपकी बात पूरी तरह समझ नहीं आई। क्या आप फसल सलाह, मंडी भाव, लोन या मौसम के बारे में पूछ रहे हैं?" # TODO: Localize

        except Exception as core_logic_error:
             logger.exception(f"Error during core logic execution for intent {intent}: {core_logic_error}")
             response_text = "जानकारी प्राप्त करने में एक समस्या हुई है। कृपया बाद में प्रयास करें।" # TODO: Localize

        # --- Generate IVR Response ---
        # Decide if the conversation ends here or continues
        # For simplicity, most intents end the call here. Loan/Linkage might need more turns.
        logger.info(f"Response for {caller_id}: '{response_text}'")
        ivr_response = {
            "action": "SPEAK_AND_HANGUP", # Or SPEAK_AND_LISTEN for multi-turn
            "payload": {
                "text_to_speak": response_text,
                "language": lang
            }
        }
        # For Twilio TwiML:
        # response = VoiceResponse()
        # response.say(response_text, language=lang)
        # response.hangup()
        # return Response(str(response), mimetype='text/xml')

        return jsonify(ivr_response)

    except Exception as e:
        logger.exception(f"Error in /ivr/handle-query: {e}")
        error_response = {
            "action": "SPEAK_AND_HANGUP",
            "payload": {"text_to_speak": "क्षमा करें, आपकी पूछताछ संसाधित करने में कोई त्रुटि हुई।", "language": config.DEFAULT_LANGUAGE}
        }
        return jsonify(error_response), 500


@api_bp.route('/whatsapp/message', methods=['POST'])
def handle_whatsapp_message():
    """
    Endpoint to handle incoming WhatsApp messages (e.g., via Twilio WhatsApp API).
    Primarily for image-based disease detection.
    """
    logger = current_app.logger
    try:
        # --- Parse Incoming WhatsApp Webhook Data ---
        # Structure depends heavily on the provider (Twilio, Gupshup, etc.)
        # Example for Twilio (might differ):
        # sender_id = request.form.get('From') # e.g., 'whatsapp:+15551234567'
        # message_body = request.form.get('Body')
        # num_media = int(request.form.get('NumMedia', 0))
        # media_url = request.form.get('MediaUrl0') if num_media > 0 else None
        # media_type = request.form.get('MediaContentType0') if num_media > 0 else None

        # Simulating from JSON body for testing:
        if not request.is_json:
             logger.error("WhatsApp handler: Request must be JSON for simulation.")
             return jsonify({"error": "Request must be JSON"}), 400

        sender_id = request.json.get('sender_id') # e.g., "whatsapp:+1555..."
        message_body = request.json.get('message_body')
        media_url = request.json.get('media_url') # URL of the image/video
        media_type = request.json.get('media_type', 'image/jpeg' if media_url else None) # MIME type

        if not sender_id:
             logger.error("WhatsApp handler: Missing sender_id.")
             return jsonify({"error": "Missing sender_id"}), 400

        logger.info(f"WhatsApp message received from: {sender_id}")
        farmer_context = get_farmer_context(sender_id) # Use whatsapp number as ID
        lang = farmer_context.get('language', config.DEFAULT_LANGUAGE)
        location = farmer_context.get("location", "Unknown")
        crop = farmer_context.get("current_crop", "गेहूं")

        response_text = "नमस्ते! फसल रोग निदान के लिए कृपया फोटो भेजें। अन्य जानकारी के लिए अपना सवाल लिखें।" # TODO: Localize

        # --- Handle Image Input ---
        if media_url and media_type and media_type.startswith('image/'):
            logger.info(f"Received image from {sender_id}: {media_url} ({media_type})")
            try:
                # !! REPLACE WITH ACTUAL IMAGE DOWNLOAD AND PROCESSING !!
                # response = requests.get(media_url, stream=True, auth=(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)) # Auth might be needed for Twilio media
                # response.raise_for_status()
                # image_data = response.content # Read image bytes
                image_data_placeholder = f"simulated_image_bytes_from_{media_url}"

                # Call disease detection logic
                diagnosis_result = disease_detection.detect_disease_from_image(image_data_placeholder)
                response_text = f"{diagnosis_result.get('diagnosis', 'विश्लेषण विफल')}\nसलाह: {diagnosis_result.get('advice', 'कोई सलाह उपलब्ध नहीं।')}" # TODO: Localize

            except requests.exceptions.RequestException as req_err:
                 logger.error(f"Failed to download image {media_url}: {req_err}")
                 response_text = "क्षमा करें, आपकी भेजी गई छवि को डाउनलोड करने में समस्या हुई।" # TODO: Localize
            except Exception as proc_err:
                 logger.exception(f"Error processing image from {media_url}: {proc_err}")
                 response_text = "क्षमा करें, छवि का विश्लेषण करने में एक त्रुटि हुई।" # TODO: Localize

        # --- Handle Text Input ---
        elif message_body:
            logger.info(f"Received text from {sender_id}: '{message_body}'")
            update_farmer_context(sender_id, {"last_query": message_body})
            # Optional: Handle text queries via WhatsApp too (reuse NLU/intent logic)
            # intent_data = language.understand_intent(message_body, language_code=lang)
            # intent = intent_data.get("intent", "UNKNOWN")
            # ... route to core logic based on intent ...
            # For now, just acknowledge text if not an image:
            response_text = f"आपने लिखा: '{message_body}'. रोग निदान के लिए फोटो भेजें या विशिष्ट सलाह के लिए कॉल करें।" # TODO: Localize

        else:
            logger.warning(f"Received empty or non-image/text message from {sender_id}")
            # Keep default welcome/instruction message

        # --- Send Reply via WhatsApp ---
        # !! REPLACE WITH ACTUAL WHATSAPP SENDING !!
        logger.info(f"Sending WhatsApp reply to {sender_id}: '{response_text}'")
        telephony.send_whatsapp_message(sender_id, response_text)

        # Return acknowledgment to the webhook provider (usually an empty 200 OK or specific format)
        return jsonify({"status": "received", "reply_simulated": response_text}), 200

    except Exception as e:
        logger.exception(f"Error in /whatsapp/message: {e}")
        # Don't try to send a WhatsApp error message here usually,
        # just return 500 so the provider knows delivery failed.
        return jsonify({"status": "error"}), 500