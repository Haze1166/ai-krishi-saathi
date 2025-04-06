import random
from flask import current_app

def check_loan_eligibility(farmer_context):
    """
    Placeholder: Checks loan eligibility based on farmer data.
    !! REPLACE with actual rules engine or API calls to financial institutions/schemes !!
    """
    logger = current_app.logger
    farmer_id = farmer_context.get('id', 'Unknown')
    logger.info(f"[SIMULATE] Finance: Checking loan eligibility for farmer: {farmer_id}")

    # --- Simulation Logic ---
    # Real system needs actual data: Land docs, Credit Score (if available), Scheme rules (KCC etc.)
    land_size = farmer_context.get('land_size_acres', 0)
    crop = farmer_context.get('current_crop', 'unknown')
    # requested_amount = farmer_context.get('requested_amount') # Need to ask this via IVR

    eligible = False
    max_eligible_amount = 0
    message = "आपकी लोन पात्रता जांचने के लिए अधिक जानकारी आवश्यक है।" # Default
    potential_lenders = []

    # Basic simulation rule (e.g., based on land size for KCC type loan)
    if land_size > 0.5 and crop != 'unknown': # Minimum land holding
        # Simulate eligibility amount (e.g., Rs 10000 per acre, capped)
        base_eligibility_per_acre = random.randint(8000, 15000)
        max_eligible_amount = min(land_size * base_eligibility_per_acre, 150000) # Cap example
        eligible = True
        potential_lenders = random.sample(["स्थानीय सहकारी बैंक", "निकटतम राष्ट्रीयकृत बैंक", "एबीसी माइक्रोफाइनेंस"], k=random.randint(1,2))
        lender_string = " या ".join(potential_lenders)
        message = f"अनुमानित पात्रता: आप लगभग ₹{int(max_eligible_amount):,} तक के कृषि लोन (जैसे किसान क्रेडिट कार्ड) के लिए पात्र हो सकते हैं। अधिक जानकारी और आवेदन के लिए {lender_string} से संपर्क करें।"
    elif land_size <= 0.5:
         message = "किसान क्रेडिट कार्ड जैसी योजनाओं के लिए आमतौर पर अधिक भूमि की आवश्यकता हो सकती है। स्वयं सहायता समूह या माइक्रोफाइनेंस योजनाओं के बारे में पता करें।"
    else:
         message = "आपकी लोन पात्रता जांचने के लिए फसल और भूमि की जानकारी आवश्यक है।"

    result = {
        "eligible": eligible,
        "max_eligible_amount": int(max_eligible_amount),
        "message": message,
        "potential_lenders": potential_lenders
    }
    logger.info(f"[SIMULATE] Loan Eligibility Result for {farmer_id}: {result}")
    return result


def get_insurance_info(crop, location):
    """
    Placeholder: Provides information about relevant crop insurance schemes (like PMFBY).
    !! REPLACE with dynamic fetching of scheme details, deadlines, etc. from official sources !!
    """
    logger = current_app.logger
    logger.info(f"[SIMULATE] Finance: Fetching insurance info for {crop} in {location}")

    # --- Static Simulation ---
    # Real system needs to fetch current deadlines, premium details etc. for PMFBY based on crop/location/season
    scheme_name = "प्रधानमंत्री फसल बीमा योजना (PMFBY)"
    info = f"{crop} के लिए {scheme_name} उपलब्ध हो सकती है।"
    info += " इस योजना के तहत, प्राकृतिक आपदाओं, कीटों और रोगों से फसल को होने वाले नुकसान के लिए बीमा कवरेज मिलता है।"
    info += " आवेदन करने की अंतिम तिथि आमतौर पर बुवाई के मौसम (खरीफ/रबी) के अनुसार निर्धारित होती है।"
    info += " अधिक जानकारी, प्रीमियम और आवेदन प्रक्रिया के लिए कृपया अपने बैंक, सहकारी समिति, कॉमन सर्विस सेंटर (CSC) या कृषि विभाग से तुरंत संपर्क करें।"
    # Add specific deadline if known (e.g., "रबी फसलों के लिए अंतिम तिथि आमतौर पर दिसंबर में होती है।")

    result = {"scheme_name": scheme_name, "info": info}
    logger.info(f"[SIMULATE] Insurance Info Result: {result}")
    return result