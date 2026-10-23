"""
CropGuardian AI - Persistence Service
Manages local SQLite storage for pest reports, diagnostic history,
and baseline agricultural field intelligence.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crop_guardian.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Pest reports table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pest_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pest_name TEXT NOT NULL,
        crop_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        location_name TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        notes TEXT,
        is_simulated INTEGER NOT NULL DEFAULT 0,
        reporter_name TEXT DEFAULT 'Anonymous Farmer',
        verification_status TEXT DEFAULT 'Pending Verification'
    )
    """)
    
    # Crop diagnosis history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crop_diagnoses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_name TEXT NOT NULL,
        symptoms TEXT,
        primary_diagnosis TEXT NOT NULL,
        confidence REAL NOT NULL,
        diagnosis_category TEXT NOT NULL,
        evidence TEXT,
        uncertainty_note TEXT,
        nutrient_summary TEXT,
        action_plan TEXT,
        timestamp TEXT NOT NULL,
        is_simulated INTEGER NOT NULL DEFAULT 0
    )
    """)
    
    conn.commit()
    
    # Check if pest_reports is empty; if so, seed realistic baseline data
    cursor.execute("SELECT COUNT(*) as cnt FROM pest_reports")
    count = cursor.fetchone()["cnt"]
    if count == 0:
        seed_baseline_pest_data(conn)
        
    conn.close()

def seed_baseline_pest_data(conn):
    """
    Seeds realistic demonstration reports in key agricultural clusters.
    All seeded data has is_simulated = 1.
    """
    cursor = conn.cursor()
    now = datetime.now()
    
    # Realistic regional cluster centers (e.g., Punjab / Indus Basin Agricultural Belt)
    # Cluster 1: Faisalabad Agricultural Belt (Wheat / Corn / Sugarcane - Fall Armyworm outbreak)
    # Cluster 2: Multan / Khanewal Cotton Belt (Cotton - Whitefly / Bollworm cluster)
    # Cluster 3: Sargodha Citrus Belt (Citrus - Citrus Psyllid / Fruit Fly cluster)
    # Cluster 4: Scattered baseline reports (outliers)
    
    clusters = [
        {
            "name": "Faisalabad Agro Belt",
            "lat": 31.4504,
            "lon": 73.1350,
            "pests": ["Fall Armyworm", "Maize Stem Borer"],
            "crops": ["Maize", "Wheat"],
            "severity_weights": ["High", "Severe", "Medium"],
            "count": 14,
            "radius_deg": 0.08
        },
        {
            "name": "Khanewal Cotton Zone",
            "lat": 30.3000,
            "lon": 71.9300,
            "pests": ["Cotton Whitefly", "Pink Bollworm"],
            "crops": ["Cotton", "Soybean"],
            "severity_weights": ["High", "Severe", "High"],
            "count": 12,
            "radius_deg": 0.07
        },
        {
            "name": "Sargodha Citrus Orchards",
            "lat": 32.0836,
            "lon": 72.6711,
            "pests": ["Asian Citrus Psyllid", "Fruit Fly"],
            "crops": ["Citrus", "Vegetables"],
            "severity_weights": ["Medium", "High", "Low"],
            "count": 9,
            "radius_deg": 0.06
        },
        {
            "name": "Gujranwala Rice Belt",
            "lat": 32.1877,
            "lon": 74.1945,
            "pests": ["Rice Leaf Folder", "Brown Planthopper"],
            "crops": ["Rice", "Wheat"],
            "severity_weights": ["Medium", "Low", "Medium"],
            "count": 8,
            "radius_deg": 0.09
        }
    ]
    
    reports = []
    
    for c in clusters:
        for i in range(c["count"]):
            # Scatter coordinates within agricultural perimeter
            lat_jitter = random.gauss(0, c["radius_deg"] / 2.2)
            lon_jitter = random.gauss(0, c["radius_deg"] / 2.2)
            lat = round(c["lat"] + lat_jitter, 5)
            lon = round(c["lon"] + lon_jitter, 5)
            
            pest = random.choice(c["pests"])
            crop = random.choice(c["crops"])
            severity = random.choice(c["severity_weights"])
            hours_ago = random.randint(2, 96)
            report_time = (now - timedelta(hours=hours_ago)).strftime("%Y-%m-%d %H:%M")
            
            notes = f"Observed active infestation on young {crop.lower()} leaves. Field scouting confirmed {severity.lower()} nymph activity."
            verification = "Verified by Field Scouting" if random.random() > 0.3 else "Community Report"
            
            reports.append((
                pest, crop, severity, lat, lon, c["name"],
                report_time, notes, 1, "Simulated Ag Station", verification
            ))
            
    # Add a few isolated outlier reports
    outliers = [
        ("Desert Locust", "Wheat", "High", 31.95, 71.30, "Bhakkar Thal Region", (now - timedelta(hours=14)).strftime("%Y-%m-%d %H:%M"), "Isolated swarm scouting report in sandy tract.", 1, "Simulated Sentinel", "Unverified"),
        ("Aphids", "Mustard", "Low", 32.55, 73.20, "Mandi Bahauddin", (now - timedelta(hours=36)).strftime("%Y-%m-%d %H:%M"), "Minor colonial buildup on upper racemes.", 1, "Simulated Sentinel", "Community Report"),
        ("Fall Armyworm", "Maize", "Medium", 30.90, 72.40, "Toba Tek Singh", (now - timedelta(hours=20)).strftime("%Y-%m-%d %H:%M"), "Early whorl feeding symptoms spotted.", 1, "Simulated Sentinel", "Verified by Field Scouting")
    ]
    reports.extend(outliers)
    
    cursor.executemany("""
    INSERT INTO pest_reports (
        pest_name, crop_type, severity, latitude, longitude,
        location_name, timestamp, notes, is_simulated, reporter_name, verification_status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, reports)
    
    conn.commit()

def save_pest_report(pest_name, crop_type, severity, latitude, longitude, location_name, notes, is_simulated=0, reporter_name="Farmer"):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("""
    INSERT INTO pest_reports (
        pest_name, crop_type, severity, latitude, longitude,
        location_name, timestamp, notes, is_simulated, reporter_name, verification_status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        pest_name, crop_type, severity, latitude, longitude,
        location_name, now_str, notes, is_simulated, reporter_name, "Farmer Submitted (Pending)"
    ))
    conn.commit()
    report_id = cursor.lastrowid
    conn.close()
    return report_id

def get_all_pest_reports():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, pest_name, crop_type, severity, latitude, longitude,
           location_name, timestamp, notes, is_simulated, reporter_name, verification_status
    FROM pest_reports
    ORDER BY id DESC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def save_crop_diagnosis(crop_name, symptoms, primary_diagnosis, confidence, category, evidence, uncertainty, nutrient_summary, action_plan):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("""
    INSERT INTO crop_diagnoses (
        crop_name, symptoms, primary_diagnosis, confidence,
        diagnosis_category, evidence, uncertainty_note,
        nutrient_summary, action_plan, timestamp, is_simulated
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (
        crop_name, symptoms, primary_diagnosis, confidence,
        category, evidence, uncertainty,
        json.dumps(nutrient_summary) if isinstance(nutrient_summary, (dict, list)) else str(nutrient_summary),
        json.dumps(action_plan) if isinstance(action_plan, (dict, list)) else str(action_plan),
        now_str
    ))
    conn.commit()
    diag_id = cursor.lastrowid
    conn.close()
    return diag_id

def get_recent_diagnoses(limit=15):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, crop_name, symptoms, primary_diagnosis, confidence,
           diagnosis_category, evidence, uncertainty_note,
           nutrient_summary, action_plan, timestamp
    FROM crop_diagnoses
    ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_database_statistics():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total_pests, SUM(CASE WHEN is_simulated = 0 THEN 1 ELSE 0 END) as user_reports FROM pest_reports")
    pest_stats = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) as total_diagnoses FROM crop_diagnoses")
    diag_stats = cursor.fetchone()
    conn.close()
    
    return {
        "total_pest_reports": pest_stats["total_pests"],
        "user_pest_reports": pest_stats["user_reports"] or 0,
        "simulated_pest_reports": pest_stats["total_pests"] - (pest_stats["user_reports"] or 0),
        "total_diagnoses": diag_stats["total_diagnoses"]
    }
