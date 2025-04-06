import datetime
import random
from flask import current_app
# Import weather module if needed for real implementation
# from . import weather

# --- Sample Data (Replace with Database/API/File loading) ---
# Consider loading from JSON or DB
CROP_CALENDAR = {
    "गेहूं": {
        "sowing_months": [10, 11], # Oct, Nov
        "stages": [
            {"name": "germination", "duration_days": 15, "advice_hi": "अंकुरण का समय। हल्की सिंचाई करें यदि मिट्टी सूखी हो।"},
            {"name": "tillering", "duration_days": 30, "advice_hi": "कल्ले निकलने का समय। पहली नाइट्रोजन (यूरिया) डालें। सिंचाई आवश्यकतानुसार।"},
            {"name": "jointing", "duration_days": 25, "advice_hi": "पौधे की बढ़वार। सिंचाई का ध्यान रखें। खरपतवार नियंत्रण करें।"},
            {"name": "heading", "duration_days": 20, "advice_hi": "बालियाँ निकल रही हैं। पोटाश दे सकते हैं। पानी की कमी न होने दें।"},
            {"name": "maturity", "duration_days": 30, "advice_hi": "दाना पक रहा है। सिंचाई बंद करें। कटाई की तैयारी करें।"},
        ]
    },
    "बाजरा": {
        "sowing_months": [6, 7], # June, July (Kharif example)
         "stages": [
            {"name": "seedling", "duration_days": 20, "advice_hi": "नर्सरी या सीधी बुवाई के बाद। हल्की सिंचाई।"},
            {"name": "vegetative", "duration_days": 35, "advice_hi": "बढ़वार का समय। नाइट्रोजन खाद दें। निराई-गुड़ाई करें।"},
            {"name": "flowering", "duration_days": 25, "advice_hi": "फूल आने का समय। सिंचाई महत्वपूर्ण है।"},
            {"name": "grain_filling", "duration_days": 30, "advice_hi": "दाना भरने का समय। नमी बनाए रखें। पक्षियों से बचाव करें।"},
        ]
    },
     "धान": { # Paddy/Rice example
        "sowing_months": [6, 7],
        "stages": [
             {"name": "nursery", "duration_days": 25, "advice_hi": "नर्सरी तैयार करें या सीधी बुवाई करें।"},
             {"name": "transplanting/tillering", "duration_days": 40, "advice_hi": "रोपाई के बाद कल्ले निकलने का समय। पानी का स्तर बनाए रखें। नाइट्रोजन दें।"},
             {"name": "panicle_initiation", "duration_days": 30, "advice_hi": "बालियाँ बनने की शुरुआत। पानी महत्वपूर्ण। पोटाश दें।"},
             {"name": "flowering_maturity", "duration_days": 35, "advice_hi": "फूल आने से पकने तक। खेत को धीरे-धीरे सुखाएं (कटाई से 10-15 दिन पहले)।"},
         ]
     }
}

def get_crop_advice(crop_name, location, farmer_context):
    """
    Provides simulated crop advice based on stage and basic weather context.
    !! REPLACE WITH REAL LOGIC using farmer's sowing date, detailed weather, soil data !!
    """
    logger = current_app.logger
    logger.info(f"Getting advice for Crop: {crop_name}, Location: {location}")

    advice_text = f"{crop_name} के लिए अभी कोई विशेष सलाह उपलब्ध नहीं है।" # Default
    current_stage_name = "Unknown"

    if crop_name not in CROP_CALENDAR:
        logger.warning(f"Crop calendar not found for: {crop_name}")
        return {"advice": advice_text, "stage": current_stage_name}

    calendar = CROP_CALENDAR[crop_name]

    # --- !! Simulation of Current Stage !! ---
    # Needs farmer's actual sowing date from farmer_context
    sowing_date_str = farmer_context.get("sowing_date")
    days_since_sowing = None
    if sowing_date_str:
        try:
            sowing_date = datetime.datetime.strptime(sowing_date_str, "%Y-%m-%d").date()
            days_since_sowing = (datetime.date.today() - sowing_date).days
        except ValueError:
            logger.warning(f"Invalid sowing date format '{sowing_date_str}' for farmer {farmer_context.get('id')}")

    if days_since_sowing is None:
        # Guess stage based on typical sowing month if sowing date unknown (highly inaccurate)
        current_month = datetime.date.today().month
        if current_month in calendar["sowing_months"]:
             days_since_sowing = random.randint(5, 25) # Early stage guess
        else:
             # Crude guess based on cycle - needs improvement
             days_since_sowing = random.randint(30, 90)
        logger.info(f"Sowing date unknown/invalid. Simulating days since sowing: {days_since_sowing}")


    if days_since_sowing is not None and days_since_sowing >= 0:
        elapsed_days = 0
        stage_found = False
        for stage in calendar['stages']:
            stage_end_day = elapsed_days + stage['duration_days']
            if days_since_sowing <= stage_end_day:
                advice_text = stage['advice_hi']
                current_stage_name = stage['name']
                stage_found = True
                break
            elapsed_days = stage_end_day
        if not stage_found: # If past last stage
             advice_text = f"{crop_name} की फसल संभवतः कटाई के लिए तैयार है या कट चुकी है।"
             current_stage_name = "Harvest/Post-Harvest"

    # --- Add Simulated Weather Context ---
    # In real implementation, call weather.get_weather_forecast(location)
    simulated_weather_condition = random.choice(["rain_soon", "dry_spell", "normal"])
    weather_advice = ""
    if simulated_weather_condition == "rain_soon" and "सिंचाई" in advice_text:
        weather_advice = " अगले 2-3 दिनों में बारिश की संभावना है, इसलिए सिंचाई अभी टाल सकते हैं।"
    elif simulated_weather_condition == "dry_spell" and "सिंचाई" in advice_text:
        weather_advice = " मौसम शुष्क रहने की संभावना है, सिंचाई का विशेष ध्यान दें।"

    final_advice = f"({crop_name} - अवस्था: {current_stage_name}) {advice_text}{weather_advice}"
    logger.info(f"Generated advice: {final_advice}")

    return {"advice": final_advice, "stage": current_stage_name}


def get_general_qna_answer(query_text, crop=None, location=None):
    """
    Placeholder for answering general farming questions.
    !! REPLACE with Knowledge Base lookup, RAG, or LLM call !!
    """
    logger = current_app.logger
    logger.info(f"Answering QnA: '{query_text}' (Crop: {crop}, Loc: {location})")
    query_lower = query_text.lower()
    answer = "इस प्रश्न का उत्तर देने के लिए मेरे पास अभी पर्याप्त जानकारी नहीं है। आप कृषि विशेषज्ञ से संपर्क कर सकते हैं।" # Default

    # --- Simple Rule-Based Simulation ---
    if "बीज" in query_text or "seed" in query_lower:
        crop_str = f"{crop} के " if crop else ""
        answer = f"{crop_str}उन्नत किस्मों के बीज के लिए अपने नजदीकी कृषि विज्ञान केंद्र (KVK) या प्रमाणित बीज विक्रेता से संपर्क करें।"
    elif "दवा" in query_text or "pesticide" in query_lower or "खरपतवार" in query_text or "weed" in query_lower:
        answer = "किसी भी कीटनाशक या खरपतवारनाशक का प्रयोग करने से पहले कृषि विशेषज्ञ से सलाह अवश्य लें। सही दवा और मात्रा का प्रयोग महत्वपूर्ण है।"
    elif "मौसम" in query_text or "weather" in query_lower:
         answer = "मौसम की विस्तृत जानकारी के लिए आप मौसम संबंधी प्रश्न पूछ सकते हैं।" # Redirect to weather intent
    elif "मिट्टी जांच" in query_text or "soil test" in query_lower:
         answer = "मिट्टी की जांच कराना बहुत फायदेमंद है। इससे पोषक तत्वों की सही जानकारी मिलती है। आप अपने ब्लॉक के कृषि विभाग या KVK में संपर्क कर सकते हैं।"

    logger.info(f"Generated QnA answer: {answer}")
    return {"answer": answer}