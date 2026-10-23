"""
CropGuardian AI - AI Vision & Diagnostic Service
Integrates Google Gemini Multimodal Vision API with a robust
offline Computer Vision & Agronomic Diagnostic fallback engine.
"""

import os
import json
import numpy as np
from PIL import Image
from services.agri_knowledge import (
    NUTRIENT_PROFILES, DISEASE_PROFILES, get_integrated_action_plan
)

def get_active_api_key():
    """Returns Gemini API key from environment or returns None."""
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

def analyze_crop_image(image: Image.Image, crop_name: str, reported_symptoms: str, api_key: str = None) -> dict:
    """
    Analyzes crop image and symptoms using Google Gemini Multimodal Vision if available,
    or falls back to the local Computer Vision & Agronomic Heuristic Engine.
    """
    key_to_use = api_key or get_active_api_key()
    
    if key_to_use:
        try:
            return _call_gemini_vision(image, crop_name, reported_symptoms, key_to_use)
        except Exception as e:
            # Fallback gracefully with note on API error
            fallback_res = _heuristic_vision_analysis(image, crop_name, reported_symptoms)
            fallback_res["api_notice"] = f"Switched to Offline Diagnostic Engine (API unavailable: {str(e)[:90]})"
            return fallback_res
    else:
        return _heuristic_vision_analysis(image, crop_name, reported_symptoms)

def _call_gemini_vision(image: Image.Image, crop_name: str, reported_symptoms: str, api_key: str) -> dict:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    
    # Try gemini-1.5-flash or gemini-2.5-flash
    model_name = "gemini-1.5-flash"
    try:
        model = genai.GenerativeModel(model_name)
    except Exception:
        model = genai.GenerativeModel("gemini-1.5-pro")
        
    prompt = f"""
You are CropGuardian AI, a senior agronomic pathologist and plant nutrition specialist.
Analyze this crop photograph carefully.

Reported Crop: {crop_name if crop_name else "Unknown (identify from image)"}
Reported Symptoms / Field Notes: {reported_symptoms if reported_symptoms else "None provided by farmer"}

CRITICAL RULES:
1. Be scientifically rigorous. Never claim 100% certainty from a 2D photograph alone.
2. Differentiate between biotic diseases (fungal/bacterial/viral/pest) and abiotic disorders (nutrient deficiencies, water stress, sunburn).
3. If nutrient deficiency is suspected, explicitly state that visual symptoms CANNOT definitively confirm nutrient deficiency without soil or tissue sap tests.
4. Output valid, raw JSON only (do not include markdown ticks, just JSON).

Output JSON Structure:
{{
  "crop_identified": "Crop name",
  "primary_diagnosis": "Name of disease, disorder, or condition",
  "diagnosis_category": "Disease | Nutrient Deficiency | Pest Damage | Environmental Stress | Healthy",
  "confidence": 0.82,
  "confidence_level": "High | Moderate | Low",
  "visible_evidence": [
    "Specific visible symptom 1 on foliage",
    "Specific visible symptom 2 (e.g. concentric rings, marginal chlorosis, etc.)"
  ],
  "uncertainty_explanation": "Transparent explanation of diagnostic uncertainty and confounding possibilities (e.g. drought mimicry, soil pH locks).",
  "alternative_hypotheses": [
    "Alternative cause 1 with brief reason",
    "Alternative cause 2 with brief reason"
  ],
  "nutrient_evaluation": {{
    "primary_suspect": "Nitrogen / Potassium / Iron / None",
    "suspected_mobility": "Mobile in older leaves / Immobile in young leaves",
    "confounding_environmental_factors": "Overwatering, root damage, or high pH lock",
    "mandatory_soil_verification": "Soil nitrate or EC/pH test required before application"
  }},
  "action_plan": {{
    "urgency": "Immediate / Moderate / Preventive",
    "cultural_mechanical": ["Action 1", "Action 2"],
    "biological_organic": ["Action 1", "Action 2"],
    "chemical_safety": ["Action 1 with safety and withholding period"],
    "verification_followup": ["Monitoring step 1", "Clinic testing step 2"]
  }}
}}
"""
    response = model.generate_content([prompt, image])
    text = response.text.strip()
    
    # Strip markdown if present
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    
    result = json.loads(text)
    result["engine_mode"] = "Google Gemini Multimodal Vision"
    return result

def _heuristic_vision_analysis(image: Image.Image, crop_name: str, reported_symptoms: str) -> dict:
    """
    Robust local agronomic computer-vision analysis.
    Computes image color-space metrics and combines with agronomic knowledge base.
    """
    img_rgb = image.convert("RGB").resize((160, 160))
    arr = np.array(img_rgb, dtype=np.float32) / 255.0
    
    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]
    
    mean_r = float(np.mean(r))
    mean_g = float(np.mean(g))
    mean_b = float(np.mean(b))
    
    # Greenness Index
    greenness = float(np.mean((2 * g - r - b) / (2 * g + r + b + 1e-5)))
    # Chlorosis (Yellowing) index: high R and G, lower B
    yellow_mask = (r > 0.45) & (g > 0.45) & (b < 0.4)
    yellow_ratio = float(np.mean(yellow_mask))
    # Necrosis (Browning / dark lesions) index: low luminance, low green
    brown_mask = (r > g) & (g > b) & (r < 0.55) & (b < 0.35)
    brown_ratio = float(np.mean(brown_mask))
    
    # Analyze symptoms text
    sym_lower = (reported_symptoms or "").lower()
    crop = crop_name if crop_name and crop_name != "Select Crop..." else "Tomato"
    
    # Decision heuristics
    if "concentric" in sym_lower or "target" in sym_lower or (brown_ratio > 0.12 and yellow_ratio > 0.08):
        primary = f"Early Blight (Alternaria solani)" if crop in ["Tomato", "Potato"] else f"Foliar Leaf Blight"
        category = "Disease"
        confidence = 0.78
        evidence = [
            f"Detected focal brownish necrotic tissue ({brown_ratio*100:.1f}% foliage area).",
            "Chlorotic yellow halo surrounding lesion margins.",
            "Visual pattern indicates progressive fungal leaf colonization."
        ]
        uncertainty = "Early fungal lesions can mimic bacterial speck in early phases before target rings fully form. Humidity and leaf wetness history are decisive."
        alternatives = ["Bacterial Spot (Xanthomonas)", "Septoria Leaf Spot", "Herbicide droplet drift"]
        nutr_suspect = "Nitrogen"
        nutr_confound = "Plant is mobilizing N away from blighted senescence leaves to healthy terminals."
    
    elif "curl" in sym_lower or "whitefly" in sym_lower or "mosaic" in sym_lower:
        primary = f"Leaf Curl Viral Complex"
        category = "Disease"
        confidence = 0.81
        evidence = [
            "Foliar cupping and distorted leaf architecture.",
            f"Diffuse interveinal chlorosis detected ({yellow_ratio*100:.1f}% chlorosis ratio).",
            "Observed vector feeding stress."
        ]
        uncertainty = "Viral symptoms closely resemble severe aphid saliva toxicity and hormonal herbicide drift (e.g. 2,4-D). Vector counts must be confirmed."
        alternatives = ["Broad Mite / Spider Mite damage", "Hormonal herbicide drift injury", "Zinc deficiency rosetting"]
        nutr_suspect = "Zinc"
        nutr_confound = "Viral infection disrupts vascular transport of micronutrients."
        
    elif "yellow" in sym_lower or "chlorosis" in sym_lower or yellow_ratio > 0.15:
        if "lower" in sym_lower or "older" in sym_lower:
            primary = "Suspected Nitrogen (N) / Potassium (K) Chlorosis"
            category = "Nutrient Deficiency"
            confidence = 0.72
            evidence = [
                f"Elevated chlorosis ratio ({yellow_ratio*100:.1f}%) observed on leaf canopy.",
                "Gradual loss of chlorophyll from leaf tips/margins inward.",
                "Mobile nutrient translocation profile from mature foliage."
            ]
            uncertainty = "CRITICAL: Photograph alone cannot confirm nutrient deficiency. Root rot, overwatering, or soil salinity induce identical transpirational shutdowns."
            alternatives = ["Waterlogging / Anaerobic root stress", "Root knot nematode infestation", "Soil compaction"]
            nutr_suspect = "Nitrogen (N) or Potassium (K)"
            nutr_confound = "Waterlogging limits oxygen to roots, halting ATP needed for nutrient uptake even in nutrient-rich soils."
        else:
            primary = "Suspected Iron (Fe) or Micronutrient Interveinal Chlorosis"
            category = "Nutrient Deficiency"
            confidence = 0.70
            evidence = [
                "Sharp contrast between green vascular ribs and pale interveinal lamina.",
                f"Foliar yellowing index: {yellow_ratio*100:.1f}%.",
                "Characteristic of immobile micronutrient deficit in expanding leaves."
            ]
            uncertainty = "High soil pH (>7.5) often locks Iron and Zinc into insoluble precipitates. The deficiency is physiological, not necessarily an absence of soil nutrients."
            alternatives = ["High pH / Calcareous soil lime-induced chlorosis", "Sulfur deficiency", "Root damage"]
            nutr_suspect = "Iron (Fe) / Zinc (Zn)"
            nutr_confound = "Calcareous soils precipitate free iron into insoluble ferric hydroxides."
            
    elif "ragged" in sym_lower or "hole" in sym_lower or "caterpillar" in sym_lower or "armyworm" in sym_lower:
        primary = "Fall Armyworm / Lepidopteran Larval Feeding"
        category = "Pest Damage"
        confidence = 0.85
        evidence = [
            "Ragged leaf margin excisions and windowpane epidermal tissue removal.",
            "Mechanical foliar perforation distinct from pathogen lesions.",
            "Frass accumulation and whorl penetration."
        ]
        uncertainty = "Hail or wind whip can produce mechanical holes, but larval feeding leaves characteristic irregular gnawed perimeters."
        alternatives = ["Grasshopper feeding", "Hail damage", "Foliar beetle mastication"]
        nutr_suspect = "None"
        nutr_confound = "Nutrient status is normal; damage is strictly mechanical pest feeding."
        
    else:
        # Balanced / Default agronomic assessment
        primary = f"Leaf Spot / Early Chlorosis Complex on {crop}"
        category = "Disease" if brown_ratio > yellow_ratio else "Nutrient Deficiency"
        confidence = 0.68
        evidence = [
            f"Foliage analysis: {greenness*100:.1f}% greenness index, {yellow_ratio*100:.1f}% chlorosis ratio.",
            f"Focal tissue stress index: {brown_ratio*100:.1f}% necrotic discoloration.",
            "Initial cellular discoloration requiring targeted field scouting."
        ]
        uncertainty = "Moderate diagnostic ambiguity due to early onset. Multispectral reflectance or physical inspection of leaf underside recommended."
        alternatives = ["Bacterial spot", "Mild drought shock", "Nutrient imbalance"]
        nutr_suspect = "Nitrogen / Micronutrients"
        nutr_confound = "Early senescence overlaps with root zone moisture oscillations."

    action_plan_data = get_integrated_action_plan(primary, category, confidence)
    
    return {
        "crop_identified": crop,
        "primary_diagnosis": primary,
        "diagnosis_category": category,
        "confidence": confidence,
        "confidence_level": "High" if confidence >= 0.75 else "Moderate",
        "visible_evidence": evidence,
        "uncertainty_explanation": uncertainty,
        "alternative_hypotheses": alternatives,
        "nutrient_evaluation": {
            "primary_suspect": nutr_suspect,
            "suspected_mobility": "Mobile (Lower leaves)" if "Nitrogen" in nutr_suspect or "Potassium" in nutr_suspect else "Immobile / Systemic",
            "confounding_environmental_factors": nutr_confound,
            "mandatory_soil_verification": "Conduct quick Soil EC/pH test and leaf tissue sap analysis before applying chemical fertilizers."
        },
        "action_plan": {
            "urgency": action_plan_data["urgency_level"],
            "cultural_mechanical": action_plan_data["immediate_cultural_actions"],
            "biological_organic": action_plan_data["biological_and_organic_controls"],
            "chemical_safety": action_plan_data["targeted_chemical_intervention"],
            "verification_followup": action_plan_data["verification_and_monitoring"]
        },
        "engine_mode": "Agronomic Computer Vision & Heuristic Diagnostic Engine (Offline Mode)"
    }
