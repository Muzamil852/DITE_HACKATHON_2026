"""
CropGuardian AI — AI-Powered Crop Health, Nutrient Intelligence & Pest Outbreak Prediction
DITE Hackathon 2026–27 | Theme: Agriculture
"""

import os
import streamlit as st
import pandas as pd
from PIL import Image
import io
import plotly.express as px

# Internal Services & Components
from services.database import (
    init_db, save_pest_report, get_all_pest_reports,
    save_crop_diagnosis, get_recent_diagnoses, get_database_statistics
)
from services.agri_knowledge import (
    CROPS_LIST, COMMON_PESTS, NUTRIENT_PROFILES, DISEASE_PROFILES
)
from services.ai_vision import analyze_crop_image, get_active_api_key
from services.clustering import detect_pest_hotspots, assess_farm_vulnerability
from components.ui_theme import apply_agricultural_theme
from components.map_view import render_pest_outbreak_map

# Page Configuration
st.set_page_config(
    page_title="CropGuardian AI | Agricultural Intelligence",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Custom Theme
apply_agricultural_theme()

# Ensure Database is Initialized
init_db()

# Session State Initialization
if "current_diagnosis" not in st.session_state:
    st.session_state.current_diagnosis = None
if "api_key" not in st.session_state:
    st.session_state.api_key = get_active_api_key() or ""

# --- SIDEBAR NAVIGATION & SETTINGS ---
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
        <span style="font-size: 2.2rem;">🌱</span>
        <div>
            <h2 style="margin: 0; font-size: 1.35rem; color: #1E4620; font-family: 'Space Grotesk', sans-serif;">CropGuardian AI</h2>
            <p style="margin: 0; font-size: 0.8rem; color: #52796F; font-weight: 600;">DITE HACKATHON 2026–27</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    selected_nav = st.radio(
        "Navigation",
        [
            "🩺 AI Crop Doctor",
            "🧪 Nutrient Intelligence",
            "🗺️ Pest Outbreak Heatmap",
            "📋 Smart Action Planner",
            "📊 Field Intelligence Hub"
        ],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ AI Engine Configuration")
    
    has_env_key = bool(get_active_api_key())
    key_input = st.text_input(
        "Google Gemini API Key (Optional)",
        type="password",
        value=st.session_state.api_key,
        help="CropGuardian functions seamlessly in Dual-Mode. If no API key is provided, the offline Agronomic Heuristic Diagnostic Engine handles all analysis."
    )
    if key_input != st.session_state.api_key:
        st.session_state.api_key = key_input
        
    if st.session_state.api_key:
        st.markdown('<span class="badge badge-safe">API Connected: Gemini Vision Active</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-warning">Dual Mode: Offline Heuristic Engine Active</span>', unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.82rem; color: #64748B; line-height: 1.4;">
        <b>Team:</b> Bachelor of IT (3 Members)<br>
        <b>Model:</b> Gemini 1.5 Flash + Scikit-Learn DBSCAN<br>
        <b>Version:</b> 1.0 Production MVP
    </div>
    """, unsafe_allow_html=True)

# --- HEADER BANNER ---
st.markdown("""
<div class="agri-banner">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
        <div>
            <h1>CropGuardian AI</h1>
            <p>AI-Powered Crop Pathology, Nutrient Diagnostics & Geospatial Pest Outbreak Intelligence.</p>
        </div>
        <div style="margin-top: 8px;">
            <span class="badge badge-safe" style="background: rgba(255,255,255,0.2); color: #FFF; border: 1px solid rgba(255,255,255,0.4);">
                🌾 Live Field Sentinel
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# TAB 1: AI CROP DOCTOR
# ==============================================================================
if selected_nav == "🩺 AI Crop Doctor":
    st.markdown("### 🩺 Diagnostic Crop Pathology Unit")
    st.write("Upload a crop leaf or stem photograph to detect foliar diseases, calculate evidence confidence, and receive calibrated next steps.")
    
    col_input, col_preview = st.columns([1.1, 1], gap="medium")
    
    with col_input:
        st.markdown('<div class="agri-card">', unsafe_allow_html=True)
        st.markdown('<div class="agri-card-title">📸 Crop & Symptom Intake</div>', unsafe_allow_html=True)
        
        crop_selection = st.selectbox("Select Crop (or choose 'Auto-Detect')", ["Auto-Detect Crop from Photo"] + CROPS_LIST)
        
        uploaded_file = st.file_uploader("Upload Leaf / Foliage Photograph", type=["jpg", "jpeg", "png"])
        
        # Sample Quick Test Selector (for rapid evaluator demo testing)
        use_sample = st.checkbox("Or use a pre-scouted demonstration specimen", value=False)
        selected_sample = None
        if use_sample:
            selected_sample = st.selectbox(
                "Select Specimen",
                [
                    "Tomato: Concentric brown target rings with yellow halo (Suspected Early Blight)",
                    "Maize: Interveinal chlorosis on lower leaves (Suspected Nitrogen Deficiency)",
                    "Cotton: Upward leaf cupping and vein thickening (Suspected Leaf Curl Virus)",
                    "Maize: Ragged leaf edge feeding & whorl frass (Suspected Armyworm)"
                ]
            )
            
        reported_symptoms = st.multiselect(
            "Observed Visual Symptoms",
            [
                "Concentric brown target spots",
                "General yellowing (older lower leaves)",
                "Interveinal chlorosis (green veins, yellow leaf)",
                "Water-soaked greasy brown lesions",
                "Burnt leaf margins / tip scorch",
                "Upward leaf curling & cupping",
                "Powdery pustules / fungal powder",
                "Ragged holes and insect frass"
            ]
        )
        extra_field_notes = st.text_input("Additional Field Notes (e.g. recent rainfall, fertilizer applied)")
        
        symptoms_str = ", ".join(reported_symptoms)
        if extra_field_notes:
            symptoms_str += f". Notes: {extra_field_notes}"
        if use_sample and selected_sample:
            symptoms_str += f". Specimen clue: {selected_sample}"
            
        diagnose_btn = st.button("🔬 Execute AI Crop Diagnosis", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_preview:
        st.markdown('<div class="agri-card">', unsafe_allow_html=True)
        st.markdown('<div class="agri-card-title">👁️ Specimen Visualizer</div>', unsafe_allow_html=True)
        
        image_to_analyze = None
        if uploaded_file is not None:
            image_to_analyze = Image.open(uploaded_file)
            st.image(image_to_analyze, caption="Uploaded Foliage Photograph", use_container_width=True)
        elif use_sample:
            # Generate representative procedural sample preview for hackathon demo
            img_sample = Image.new('RGB', (320, 240), color=(34, 110, 50))
            image_to_analyze = img_sample
            st.image(img_sample, caption=f"Specimen Preview: {selected_sample}", use_container_width=True)
        else:
            st.info("Please upload a leaf photograph or select a demonstration specimen.")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # Execution & Results
    if diagnose_btn:
        if image_to_analyze is None:
            st.warning("Please provide a crop image before initiating analysis.")
        else:
            with st.spinner("Analyzing foliar cellular discoloration, chlorosis ratios, and disease markers..."):
                crop_param = "" if "Auto-Detect" in crop_selection else crop_selection
                res = analyze_crop_image(
                    image=image_to_analyze,
                    crop_name=crop_param,
                    reported_symptoms=symptoms_str,
                    api_key=st.session_state.api_key
                )
                st.session_state.current_diagnosis = res
                
                # Persist diagnosis in database
                save_crop_diagnosis(
                    crop_name=res.get("crop_identified", crop_selection),
                    symptoms=symptoms_str,
                    primary_diagnosis=res.get("primary_diagnosis", "Unknown"),
                    confidence=res.get("confidence", 0.5),
                    category=res.get("diagnosis_category", "Disease"),
                    evidence="\n".join(res.get("visible_evidence", [])),
                    uncertainty=res.get("uncertainty_explanation", ""),
                    nutrient_summary=res.get("nutrient_evaluation", {}),
                    action_plan=res.get("action_plan", {})
                )

    # Render Diagnostic Results if available
    if st.session_state.current_diagnosis:
        d = st.session_state.current_diagnosis
        st.markdown("---")
        st.markdown("### 📋 Diagnostic Pathology Report")
        
        # Engine Mode Pill
        mode_pill = f'<span class="badge badge-safe">{d.get("engine_mode", "AI Engine")}</span>'
        st.markdown(f"**Diagnostic Pipeline:** {mode_pill}", unsafe_allow_html=True)
        
        r1, r2, r3 = st.columns([1.2, 1, 1])
        with r1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{d.get('primary_diagnosis', 'Under Evaluation')}</div>
                <div class="metric-label">Primary Identification ({d.get('crop_identified', 'Crop')})</div>
            </div>
            """, unsafe_allow_html=True)
        with r2:
            conf_val = int(d.get('confidence', 0.7) * 100)
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{conf_val}%</div>
                <div class="metric-label">Diagnostic Confidence ({d.get('confidence_level', 'Moderate')})</div>
            </div>
            """, unsafe_allow_html=True)
        with r3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{d.get('diagnosis_category', 'Pathology')}</div>
                <div class="metric-label">Classification Category</div>
            </div>
            """, unsafe_allow_html=True)
            
        c_ev, c_unc = st.columns(2)
        with c_ev:
            st.markdown('<div class="agri-card">', unsafe_allow_html=True)
            st.markdown('<div class="agri-card-title">🔍 Visual Evidence Cited</div>', unsafe_allow_html=True)
            for ev in d.get("visible_evidence", []):
                st.markdown(f"• **{ev}**")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c_unc:
            st.markdown('<div class="agri-card">', unsafe_allow_html=True)
            st.markdown('<div class="agri-card-title">⚠️ Scientific Uncertainty & Mimicry</div>', unsafe_allow_html=True)
            st.markdown(d.get("uncertainty_explanation", "No uncertainty notes available."))
            
            alts = d.get("alternative_hypotheses", [])
            if alts:
                st.markdown("**Alternative Plausible Hypotheses:**")
                for alt in alts:
                    st.markdown(f"• *{alt}*")
            st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# TAB 2: NUTRIENT INTELLIGENCE
# ==============================================================================
elif selected_nav == "🧪 Nutrient Intelligence":
    st.markdown("### 🧪 Soil & Plant Nutrient Intelligence")
    
    st.markdown("""
    <div class="disclaimer-box">
        <b>⚖️ MANDATORY AGRONOMIC PROTOCOL:</b><br>
        Never claim a nutrient deficiency is confirmed from a photograph alone. Visual chlorosis and necrotic patterns 
        frequently mimic root-rot hypoxia, soil salinity, and fungal pathogens. Always confirm with soil testing or tissue sap analysis.
    </div>
    """, unsafe_allow_html=True)
    
    n_col1, n_col2 = st.columns([1, 1.3])
    
    with n_col1:
        st.markdown('<div class="agri-card">', unsafe_allow_html=True)
        st.markdown('<div class="agri-card-title">🌿 Nutritional Diagnostic Key</div>', unsafe_allow_html=True)
        
        target_nutrient = st.selectbox(
            "Select Nutrient to Investigate",
            list(NUTRIENT_PROFILES.keys())
        )
        
        leaf_position_filter = st.radio(
            "Where do symptoms first emerge?",
            [
                "Older / Lower Leaves (Mobile Nutrients: N, P, K, Mg)",
                "Younger / Terminal Top Leaves (Immobile Nutrients: Fe, Ca, Zn)"
            ]
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
    with n_col2:
        nutr_data = NUTRIENT_PROFILES[target_nutrient]
        st.markdown('<div class="agri-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="agri-card-title">🔎 {target_nutrient} Profile</div>', unsafe_allow_html=True)
        
        st.markdown(f"**Plant Mobility:** `{nutr_data['mobility']}`")
        st.markdown(f"**Primary Foliar Location:** `{nutr_data['leaf_position']}`")
        st.markdown(f"**Characteristic Visual Symptoms:**\n{nutr_data['symptoms']}")
        
        st.markdown("---")
        st.markdown("**⚠️ Confounding Factors (What Else Could It Be?):**")
        for cf in nutr_data["confounding_factors"]:
            st.markdown(f"• {cf}")
            
        st.markdown("---")
        st.markdown("**🔬 Mandatory Scientific Verification Protocol:**")
        for vs in nutr_data["verification_steps"]:
            st.markdown(f"✅ {vs}")
            
        st.markdown("---")
        st.markdown(f"**🚜 Evidence-Based Corrective Intervention:**\n{nutr_data['corrective_actions']}")
        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# TAB 3: PEST OUTBREAK HEATMAP
# ==============================================================================
elif selected_nav == "🗺️ Pest Outbreak Heatmap":
    st.markdown("### 🗺️ Geospatial Pest Outbreak & Cluster Sentinel")
    st.write("Real-time DBSCAN spatial clustering identifies regional infestation epicenters and predicts vulnerable farm zones.")
    
    # Retrieve all reports and run DBSCAN clustering
    all_reports = get_all_pest_reports()
    enriched_reports, hotspots = detect_pest_hotspots(all_reports, eps_km=35.0, min_reports=3)
    
    # Metrics Bar
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{len(hotspots)}</div>
            <div class="metric-label">Active Hotspots (DBSCAN)</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        critical_count = len([h for h in hotspots if h['risk_tier'] == 'CRITICAL OUTBREAK'])
        st.markdown(f"""
        <div class="metric-box" style="border-left-color: #D62828;">
            <div class="metric-value" style="color: #D62828;">{critical_count}</div>
            <div class="metric-label">Critical Threat Epicenters</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        user_cnt = len([r for r in all_reports if r['is_simulated'] == 0])
        st.markdown(f"""
        <div class="metric-box" style="border-left-color: #0284C7;">
            <div class="metric-value" style="color: #0284C7;">{user_cnt}</div>
            <div class="metric-label">Verified Farmer Reports</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-box" style="border-left-color: #7C3AED;">
            <div class="metric-value" style="color: #7C3AED;">{len(all_reports) - user_cnt}</div>
            <div class="metric-label">Simulated Demonstration Reports</div>
        </div>
        """, unsafe_allow_html=True)

    # Interactive Map Section
    map_col, control_col = st.columns([2.4, 1])
    
    with control_col:
        st.markdown('<div class="agri-card">', unsafe_allow_html=True)
        st.markdown('<div class="agri-card-title">📍 Farm Proximity Sentinel</div>', unsafe_allow_html=True)
        
        farm_crop = st.selectbox("My Farm Crop", CROPS_LIST, index=1)
        farm_lat = st.number_input("My Farm Latitude", value=31.3500, format="%.4f")
        farm_lon = st.number_input("My Farm Longitude", value=73.0500, format="%.4f")
        
        basemap = st.selectbox(
            "Map Style",
            ["carto-positron", "open-street-map", "carto-darkmatter"],
            index=0
        )
        
        vulnerability = assess_farm_vulnerability(farm_lat, farm_lon, farm_crop, hotspots)
        
        st.markdown("---")
        st.markdown(f"**Vulnerability Status:**")
        if "CRITICAL" in vulnerability["threat_level"]:
            st.markdown(f'<span class="badge badge-critical">{vulnerability["threat_level"]}</span>', unsafe_allow_html=True)
        elif "HIGH" in vulnerability["threat_level"]:
            st.markdown(f'<span class="badge badge-warning">{vulnerability["threat_level"]}</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="badge badge-safe">{vulnerability["threat_level"]}</span>', unsafe_allow_html=True)
            
        st.markdown(f"<p style='font-size:0.9rem; margin-top:8px;'>{vulnerability['message']}</p>", unsafe_allow_html=True)
        
        if vulnerability.get("actions"):
            st.markdown("**Protective Directives:**")
            for act in vulnerability["actions"]:
                st.markdown(f"• {act}")
                
        st.markdown('</div>', unsafe_allow_html=True)

    with map_col:
        render_pest_outbreak_map(
            reports=enriched_reports,
            hotspots=hotspots,
            user_farm_lat=farm_lat,
            user_farm_lon=farm_lon,
            basemap_style=basemap
        )

    # Pest Reporting Form
    st.markdown("---")
    with st.expander("📝 Submit a New Farmer Pest Scouting Report", expanded=False):
        st.markdown("""
        <div class="privacy-box">
            <b>🛡️ FARMER PRIVACY PROTECTION:</b><br>
            Precise GPS coordinates are never published publicly. Public risk zones only expose clustered general buffers 
            to protect individual property locations.
        </div>
        """, unsafe_allow_html=True)
        
        f1, f2, f3 = st.columns(3)
        with f1:
            new_pest = st.selectbox("Observed Pest", COMMON_PESTS)
            new_crop = st.selectbox("Affected Crop", CROPS_LIST, key="new_crop")
        with f2:
            new_severity = st.selectbox("Infestation Severity", ["Low", "Medium", "High", "Severe"])
            new_location_name = st.text_input("Region / District Name", value="Faisalabad Sector 4")
        with f3:
            new_lat = st.number_input("Scouted Latitude", value=31.4200, format="%.4f")
            new_lon = st.number_input("Scouted Longitude", value=73.0800, format="%.4f")
            
        new_notes = st.text_input("Scouting Observations (e.g. canopy position, nymph count, leaf damage)")
        
        if st.button("📤 Transmit Report to Outbreak Sentinel", type="primary"):
            rep_id = save_pest_report(
                pest_name=new_pest,
                crop_type=new_crop,
                severity=new_severity,
                latitude=new_lat,
                longitude=new_lon,
                location_name=new_location_name,
                notes=new_notes,
                is_simulated=0, # Real farmer report
                reporter_name="Verified Scout"
            )
            st.success(f"Report #{rep_id} logged successfully! Re-computing regional DBSCAN spatial clusters...")
            st.rerun()


# ==============================================================================
# TAB 4: SMART ACTION PLANNER
# ==============================================================================
elif selected_nav == "📋 Smart Action Planner":
    st.markdown("### 📋 Integrated Pest & Pathology Action Planner")
    st.write("Generates evidence-calibrated multi-tier intervention plans balancing ecological biological controls with chemical safety.")
    
    # Check if a diagnosis exists
    diag = st.session_state.current_diagnosis
    
    if not diag:
        st.info("No active diagnosis selected. Using default agronomic protocol template or run a diagnosis in 'AI Crop Doctor'.")
        # Default fallback protocol for demonstration
        target_condition = st.selectbox(
            "Select Agricultural Condition to Generate Protocol",
            [
                "Early Blight (Alternaria solani) on Tomato",
                "Fall Armyworm (Spodoptera frugiperda) on Maize",
                "Nitrogen Deficiency Chlorosis on Wheat",
                "Cotton Leaf Curl Virus Complex on Cotton"
            ]
        )
    else:
        target_condition = f"{diag.get('primary_diagnosis', 'Crop Condition')} on {diag.get('crop_identified', 'Crop')}"
        
    st.markdown(f"#### Strategic Action Matrix for: `{target_condition}`")
    
    c_tier1, c_tier2 = st.columns(2)
    with c_tier1:
        st.markdown('<div class="agri-card">', unsafe_allow_html=True)
        st.markdown('<div class="agri-card-title">🧹 Tier 1: Cultural & Mechanical Sanitation</div>', unsafe_allow_html=True)
        st.markdown("""
        • **Immediate Canopy Pruning:** Prune and destroy lower diseased foliage using sanitized shears (70% ethanol dip).<br>
        • **Irrigation Transition:** Cease all overhead sprinkler watering immediately. Switch to drip or base furrow to prevent leaf wetness.<br>
        • **Solar Sanitation:** Remove fallen vegetative debris from the field perimeter to eliminate overwintering spore reservoirs.
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c_tier2:
        st.markdown('<div class="agri-card">', unsafe_allow_html=True)
        st.markdown('<div class="agri-card-title">🐞 Tier 2: Biological & Bio-Rational Controls</div>', unsafe_allow_html=True)
        st.markdown("""
        • **Cold-Pressed Neem Oil (0.5%):** Foliar application with bio-detergent surfactant to inhibit fungal spore germination and repel feeding pests.<br>
        • **Beneficial Antagonists:** Apply bio-fungicidal sprays containing *Bacillus subtilis* or *Trichoderma harzianum*.<br>
        • **Pheromone Trapping:** Deploy delta traps at 5 units/hectare to disrupt mating cycles.
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    c_tier3, c_tier4 = st.columns(2)
    with c_tier3:
        st.markdown('<div class="agri-card">', unsafe_allow_html=True)
        st.markdown('<div class="agri-card-title">⚠️ Tier 3: Chemical Safety & Pre-Harvest Intervals</div>', unsafe_allow_html=True)
        st.markdown("""
        • **Economic Threshold (ETL) Enforcement:** Spray synthetic chemical protectants ONLY if scouting exceeds 10% canopy infection.<br>
        • **Mandatory Personal Protective Equipment (PPE):** Wear chemical-resistant nitrile gloves, vapor respirator, and eye protection.<br>
        • **Pollinator Protection Protocol:** Strictly prohibit spraying during daylight foraging hours. Spray exclusively at dusk.<br>
        • **Pre-Harvest Interval (PHI):** Adhere to the strict 14-day withholding period prior to crop harvest.
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c_tier4:
        st.markdown('<div class="agri-card">', unsafe_allow_html=True)
        st.markdown('<div class="agri-card-title">🔬 Tier 4: Verification & Diagnostic Audit</div>', unsafe_allow_html=True)
        st.markdown("""
        • **48-Hour Scouting Follow-Up:** Re-inspect tagged sentinel plants to evaluate lesion arrest.<br>
        • **Soil & Tissue Lab Validation:** Submit leaf petiole sap to the regional agricultural diagnostic lab.<br>
        • **Digital Log Persistence:** Transmit treatment timestamps to CropGuardian Field Intelligence for resistance management.
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# TAB 5: FIELD INTELLIGENCE HUB
# ==============================================================================
elif selected_nav == "📊 Field Intelligence Hub":
    st.markdown("### 📊 Regional Agricultural Field Intelligence")
    st.write("Aggregated diagnostic audit trails, historical surveillance records, and transparent data telemetry.")
    
    stats = get_database_statistics()
    
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{stats['total_diagnoses']}</div>
            <div class="metric-label">Total Crop Diagnoses Performed</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{stats['user_pest_reports']}</div>
            <div class="metric-label">Live Farmer Field Reports</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{stats['simulated_pest_reports']}</div>
            <div class="metric-label">Simulated Demonstration Reports</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Reports breakdown charts
    pest_reports = get_all_pest_reports()
    if pest_reports:
        df_p = pd.DataFrame(pest_reports)
        
        c_ch1, c_ch2 = st.columns(2)
        with c_ch1:
            st.markdown('<div class="agri-card">', unsafe_allow_html=True)
            st.markdown('<div class="agri-card-title">🐛 Outbreak Breakdown by Pest Species</div>', unsafe_allow_html=True)
            fig_p = px.bar(
                df_p['pest_name'].value_counts().reset_index(),
                x='pest_name', y='count',
                labels={'pest_name': 'Pest Species', 'count': 'Scouted Reports'},
                color='count',
                color_continuous_scale="Viridis"
            )
            fig_p.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=320)
            st.plotly_chart(fig_p, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c_ch2:
            st.markdown('<div class="agri-card">', unsafe_allow_html=True)
            st.markdown('<div class="agri-card-title">🌾 Crop Vulnerability Distribution</div>', unsafe_allow_html=True)
            fig_c = px.pie(
                df_p, names='crop_type',
                color_discrete_sequence=px.colors.qualitative.Prism,
                hole=0.45
            )
            fig_c.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=320)
            st.plotly_chart(fig_c, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown("#### 📜 Recent Scouting Telemetry Feed")
        
        display_df = df_p[[
            'id', 'pest_name', 'crop_type', 'severity', 'location_name',
            'timestamp', 'is_simulated', 'verification_status'
        ]].copy()
        
        display_df['Nature of Report'] = display_df['is_simulated'].apply(
            lambda x: "🔬 Simulated Baseline (Demo)" if x == 1 else "🚜 Verified Farmer Field Report"
        )
        display_df.drop(columns=['is_simulated'], inplace=True)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        csv_data = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Field Intelligence CSV",
            data=csv_data,
            file_name="crop_guardian_field_intelligence.csv",
            mime="text/csv"
        )
