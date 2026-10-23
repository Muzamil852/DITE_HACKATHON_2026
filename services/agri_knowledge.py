"""
CropGuardian AI - Agronomic Knowledge Base
Expert agricultural data covering crop diseases, visual nutrient diagnostic keys,
confounding environmental factors, and integrated pest management (IPM) protocols.
"""

CROPS_LIST = [
    "Tomato", "Maize (Corn)", "Wheat", "Potato", "Rice",
    "Cotton", "Soybean", "Citrus", "Sugarcane", "Pepper/Chilli"
]

COMMON_PESTS = [
    "Fall Armyworm", "Cotton Whitefly", "Pink Bollworm", "Maize Stem Borer",
    "Rice Leaf Folder", "Brown Planthopper", "Asian Citrus Psyllid", "Aphids",
    "Desert Locust", "Spider Mites", "Fruit Fly", "Thrips"
]

NUTRIENT_PROFILES = {
    "Nitrogen (N)": {
        "mobility": "High (Mobile in plant)",
        "leaf_position": "Older / Lower leaves first",
        "symptoms": "General uniform yellowing (chlorosis) starting from leaf tips and midribs, stunted thin stems, overall pale foliage.",
        "confounding_factors": [
            "Waterlogging / Root hypoxia (prevents N uptake even if present in soil)",
            "Drought stress (restricts transpirational pull)",
            "Nematode root galls destroying feeder roots",
            "Early blight or fungal leaf senescence"
        ],
        "verification_steps": [
            "Perform Soil Nitrate-N quick test (colorimetric test kit)",
            "Check Soil pH (optimum 6.0 - 7.0 for maximum N availability)",
            "Scout root zone for water saturation or rot"
        ],
        "corrective_actions": "Apply split-dose urea, ammonium nitrate, or well-composted organic poultry manure. Avoid heavy single doses before rainfall to prevent leaching."
    },
    "Phosphorus (P)": {
        "mobility": "High (Mobile in plant)",
        "leaf_position": "Older / Lower leaves first",
        "symptoms": "Purpling, bronzing, or abnormally dark bluish-green leaves; delayed maturity; poor root establishment and thin stalks.",
        "confounding_factors": [
            "Cold soil temperatures (<15°C) restricting root metabolism and P diffusion",
            "Severe root insect feeding (grubs/wireworms)",
            "Soil compaction restricting root volume",
            "High soil pH (>7.8) or low pH (<5.5) causing chemical fixation with Ca, Fe, or Al"
        ],
        "verification_steps": [
            "Olsen or Bray soil phosphorus extraction test",
            "Soil temperature check at 10cm depth",
            "Root architecture inspection"
        ],
        "corrective_actions": "Apply banded Diammonium Phosphate (DAP), Single Super Phosphate (SSP), or microbial phosphate-solubilizing inoculants near seed furrow."
    },
    "Potassium (K)": {
        "mobility": "High (Mobile in plant)",
        "leaf_position": "Older / Lower leaves first",
        "symptoms": "Marginal chlorosis turning into severe necrosis ('leaf scorch' or burnt edges), curling leaf tips, weak stalks prone to lodging.",
        "confounding_factors": [
            "Salinity / Chloride toxicity (exhibits identical marginal leaf burn)",
            "Severe drought and hot dry winds causing tip desiccation",
            "Bacterial leaf scorch (e.g., Xanthomonas)",
            "Over-fertilization with Magnesium or Ammonium competing for root uptake"
        ],
        "verification_steps": [
            "Soil Electrical Conductivity (EC) test to rule out salt burn",
            "Exchangeable K soil test",
            "Leaf tissue lab analysis"
        ],
        "corrective_actions": "Side-dress Potassium Sulfate (SOP) or Muriate of Potash (MOP), or apply foliar spray of 1% potassium nitrate (KNO3) during critical vegetative/bloom stages."
    },
    "Magnesium (Mg)": {
        "mobility": "High (Mobile)",
        "leaf_position": "Older / Lower leaves first",
        "symptoms": "Distinct interveinal chlorosis (veins remain dark green while tissue between turns pale yellow to reddish-purple).",
        "confounding_factors": [
            "Excessive Potassium or Calcium application inducing competitive uptake block",
            "Spider mite stippling resembling chlorotic mottling",
            "Viral vein mosaic infections"
        ],
        "verification_steps": [
            "Cation Exchange Capacity (CEC) ratio test (K:Mg balance)",
            "Tissue petiole sap analysis"
        ],
        "corrective_actions": "Apply agricultural Epsom salt (Magnesium Sulfate heptahydrate) via foliar spray (1-2%) or soil application of dolomitic limestone in acidic soils."
    },
    "Iron (Fe)": {
        "mobility": "Low (Immobile in plant)",
        "leaf_position": "Youngest / Top terminal leaves first",
        "symptoms": "Vivid, sharp interveinal chlorosis on newest leaves; leaf veins stay distinctly green creating an intricate net pattern. Severe deficiency turns whole leaf ivory white.",
        "confounding_factors": [
            "Calcareous / high pH soils (free calcium carbonate immobilizing iron)",
            "Over-compacted, poorly aerated waterlogged soil",
            "Root rot pathogens (Pythium, Phytophthora)"
        ],
        "verification_steps": [
            "Measure active lime content and soil pH (>7.5 strongly suggests lime-induced chlorosis)",
            "Visual inspection of terminal shoot flush"
        ],
        "corrective_actions": "Foliar spray of Fe-EDDHA or Fe-EDTA chelated iron. Avoid unchelated ferrous sulfate in high pH soils as it rapidly precipitates."
    },
    "Zinc (Zn)": {
        "mobility": "Intermediate / Low",
        "leaf_position": "Middle to upper young leaves",
        "symptoms": "Banding or broad bleached chlorotic strips along the midrib in monocots (white bud in maize); shortened internodes ('rosetting') and small leaves ('little leaf').",
        "confounding_factors": [
            "Excessive Phosphorus fertilization antagonizing Zn uptake",
            "Herbicide injury (e.g., ALS inhibitors causing internode shortening)",
            "Cool wet spring weather"
        ],
        "verification_steps": [
            "DTPA extractable Zinc soil test (<0.8 ppm indicates acute deficiency)",
            "Leaf tissue testing"
        ],
        "corrective_actions": "Soil application of Zinc Sulfate (ZnSO4 21% or 33%) or foliar application of chelated Zinc prior to rapid vegetative extension."
    },
    "Calcium (Ca)": {
        "mobility": "Low (Immobile)",
        "leaf_position": "New growth tips, fruit, and buds",
        "symptoms": "Blossom end rot in tomato/pepper, tip burn in leafy crops, distorted 'hooked' young leaf margins, necrosis of growing tips.",
        "confounding_factors": [
            "Erratic watering cycles (Calcium moves strictly via transpiration stream)",
            "High relative humidity shutting down transpirational pull",
            "Excessive Nitrogen causing rapid succulent vegetative growth"
        ],
        "verification_steps": [
            "Soil moisture monitoring and irrigation uniformity check",
            "Soil exchangeable Calcium test"
        ],
        "corrective_actions": "Stabilize irrigation schedule; avoid allowing soil to cycle between desiccated and flooded; apply Calcium Nitrate foliar or fertigation."
    }
}

DISEASE_PROFILES = {
    "Tomato": [
        {
            "name": "Early Blight (Alternaria solani)",
            "type": "Fungal",
            "visual_cues": "Concentric rings ('target board' pattern) on older leaves, surrounded by yellow chlorotic halo, starting low on plant canopy.",
            "progression": "Spreads upward during warm, humid conditions with repeated leaf wetting.",
            "key_distinction": "Concentric rings distinguish it from bacterial spot (water-soaked) and nutrient deficiency (uniform/interveinal)."
        },
        {
            "name": "Late Blight (Phytophthora infestans)",
            "type": "Oomycete / Water Mold",
            "visual_cues": "Rapidly expanding water-soaked greasy brown lesions on leaves and stems; white cottony fungal growth on underside in high humidity.",
            "progression": "Catastrophic collapse of foliage and brown firm rot on fruit within 48-72 hours under cool, wet weather.",
            "key_distinction": "Lacks target rings; causes fast structural collapse unlike gradual nutrient deficiency."
        },
        {
            "name": "Bacterial Spot (Xanthomonas spp.)",
            "type": "Bacterial",
            "visual_cues": "Small (1-3mm), dark brown, angular water-soaked lesions that often scab on fruit surfaces with slight yellow halos.",
            "progression": "Favored by driving rain and overhead irrigation.",
            "key_distinction": "Lesions are restricted by leaf veins (angular) rather than circular."
        },
        {
            "name": "Tomato Yellow Leaf Curl Virus (TYLCV)",
            "type": "Viral (Vector: Whitefly)",
            "visual_cues": "Severe upward leaf cupping, thickening, marked interveinal yellowing, stunted bush-like growth.",
            "progression": "Systemic viral spread; infected plants fail to set marketable fruit.",
            "key_distinction": "Cupping and vector presence distinguish it from simple nutrient chlorosis."
        }
    ],
    "Maize (Corn)": [
        {
            "name": "Northern Corn Leaf Blight (Exserohilum turcicum)",
            "type": "Fungal",
            "visual_cues": "Long, elliptical, cigar-shaped grayish-green to tan lesions (2.5 to 15 cm long) parallel to leaf veins.",
            "progression": "Extensive blighting reduces photosynthetic area dramatically during grain fill.",
            "key_distinction": "Cigar-shaped lesions run parallel to veins; nutrient deficiency affects entire leaf margins or midribs."
        },
        {
            "name": "Common Rust (Puccinia sorghi)",
            "type": "Fungal",
            "visual_cues": "Golden-brown to cinnamon-brown powdery pustules on both upper and lower leaf surfaces.",
            "progression": "Spores erupt through leaf epidermis under moderate temperatures and high humidity.",
            "key_distinction": "Powdery pustules leave reddish residue when wiped with a finger."
        },
        {
            "name": "Fall Armyworm Damage (Spodoptera frugiperda)",
            "type": "Pest Larval Damage",
            "visual_cues": "Ragged 'windowpane' feeding on young leaves, large irregular holes, heavy sawdust-like frass accumulated inside whorl.",
            "progression": "Larvae bore deep into whorl and developing ear tips.",
            "key_distinction": "Direct mechanical tissue removal and frass distinguishes from fungal necrosis."
        }
    ],
    "Wheat": [
        {
            "name": "Stripe Rust / Yellow Rust (Puccinia striiformis)",
            "type": "Fungal",
            "visual_cues": "Narrow yellow stripes or linear rows of bright yellow pustules along leaf blades.",
            "progression": "Spreads rapidly during cool, moist periods.",
            "key_distinction": "Strict linear row pattern following veins distinguishes from non-pathogenic streaks."
        },
        {
            "name": "Tan Spot (Pyrenophora tritici-repentis)",
            "type": "Fungal",
            "visual_cues": "Small tan oval spots with distinct yellow halo, expanding into irregular blotches with small dark center.",
            "progression": "Stubble-borne inoculum moves up canopy with rain splash.",
            "key_distinction": "Yellow halo surrounding dark central pinpoint."
        }
    ],
    "Potato": [
        {
            "name": "Late Blight (Phytophthora infestans)",
            "type": "Oomycete",
            "visual_cues": "Dark brown/black water-soaked lesions expanding rapidly; white fuzzy growth underneath in damp mornings.",
            "progression": "Complete vine defoliation and tuber rotting in wet seasons.",
            "key_distinction": "Fast blighting following rain."
        },
        {
            "name": "Early Blight (Alternaria solani)",
            "type": "Fungal",
            "visual_cues": "Concentric ring lesions surrounded by chlorotic yellow zone on lower canopy leaves.",
            "progression": "Gradual defoliation beginning at plant senescence.",
            "key_distinction": "Target rings; slower progression than late blight."
        }
    ],
    "Rice": [
        {
            "name": "Rice Blast (Magnaporthe oryzae)",
            "type": "Fungal",
            "visual_cues": "Spindle-shaped or diamond-shaped lesions with gray/whitish centers and reddish-brown borders.",
            "progression": "Attacks leaves, nodes, and panicle neck causing 'neck blast' and lodging.",
            "key_distinction": "Diamond-shaped eye lesions."
        },
        {
            "name": "Bacterial Panicle Blight (Burkholderia glumae)",
            "type": "Bacterial",
            "visual_cues": "White to straw-colored florets, panicles remain erect because grains fail to fill.",
            "progression": "Favored by night temperatures above 24°C during heading.",
            "key_distinction": "Discolored empty florets on otherwise green plants."
        }
    ],
    "Cotton": [
        {
            "name": "Cotton Leaf Curl Virus (CLCuV)",
            "type": "Viral (Vector: Whitefly)",
            "visual_cues": "Upward or downward leaf curling, swollen/thickened veins, leafy enations (cup-shaped outgrowths) on underside.",
            "progression": "Severe stunting, reduced flowering and boll shedding.",
            "key_distinction": "Vein thickening and enations are diagnostic."
        },
        {
            "name": "Bacterial Blight / Angular Leaf Spot (Xanthomonas)",
            "type": "Bacterial",
            "visual_cues": "Angular water-soaked spots bounded by leaf veins; can cause black arm lesions on stems and boll rot.",
            "progression": "Transmitted by wind-driven rain and infected seeds.",
            "key_distinction": "Strictly angular margins matching vein boundaries."
        }
    ]
}

def get_integrated_action_plan(diagnosis_name, category, confidence):
    """
    Returns an actionable, evidence-calibrated multi-tier agronomic plan.
    """
    plan = {
        "urgency_level": "High" if confidence > 0.7 else "Moderate",
        "immediate_cultural_actions": [
            "Isolate visibly infected plant sections; prune severely damaged lower foliage with sanitized tools.",
            "Adjust irrigation: switch from overhead sprinkler to drip or furrow to eliminate leaf wetness duration.",
            "Ensure field drainage to eliminate stagnant water pockets that favor root rot and spore germination."
        ],
        "biological_and_organic_controls": [
            "Apply cold-pressed organic Neem oil (0.5% concentration with bio-detergent surfactant) as early anti-feedant and fungistatic barrier.",
            "Introduce or conserve natural predators (ladybird beetles, lacewings) if sucking pests are implicated.",
            "Consider bio-fungicide sprays containing Bacillus subtilis or Trichoderma viride."
        ],
        "targeted_chemical_intervention": [
            "If disease pressure crosses economic threshold (ETL > 10% canopy affected), apply label-approved protectant.",
            "MANDATORY SAFETY: Wear chemical-resistant gloves, eye goggles, and respirator mask.",
            "POLLINATOR PROTECTION: Never spray during peak bee foraging hours; spray strictly at dawn or dusk.",
            "Adhere strictly to Pre-Harvest Intervals (PHI) specified on official agrochemical packaging."
        ],
        "verification_and_monitoring": [
            "Re-scout tagged diagnostic plants 48 to 72 hours post-treatment to evaluate lesion arrest.",
            "Deploy yellow sticky traps for vector monitoring (whiteflies, thrips, aphids).",
            "Send leaf samples in paper bags to the regional agricultural extension diagnostic clinic for PCR or plating confirmation if symptoms persist."
        ]
    }
    return plan
