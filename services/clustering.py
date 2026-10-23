"""
CropGuardian AI - Geospatial Pest Outbreak & Clustering Service
Uses Scikit-Learn DBSCAN to cluster pest reports into active outbreak hotspots,
calculates risk zones, and evaluates nearby farm vulnerability.
"""

import math
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

def haversine_distance_km(lat1, lon1, lat2, lon2):
    """Calculates great-circle distance between two GPS coordinates in kilometers."""
    R = 6371.0 # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def detect_pest_hotspots(reports_list, eps_km=35.0, min_reports=3):
    """
    Applies DBSCAN clustering on GPS coordinates of pest reports.
    Returns:
      - enriched_reports: list of reports with 'cluster_id' and 'is_hotspot'
      - hotspots_summary: list of active cluster summaries with centroids, radii, and risk scores
    """
    if not reports_list or len(reports_list) < min_reports:
        return reports_list, []
    
    df = pd.DataFrame(reports_list)
    coords = df[['latitude', 'longitude']].to_numpy()
    
    # Convert lat/lon to radians for Haversine metric
    coords_rad = np.radians(coords)
    # Earth radius ~ 6371 km
    eps_rad = eps_km / 6371.0
    
    db = DBSCAN(eps=eps_rad, min_samples=min_reports, metric='haversine')
    labels = db.fit_predict(coords_rad)
    
    df['cluster_id'] = labels
    df['is_hotspot'] = labels != -1
    
    hotspots_summary = []
    unique_clusters = set(labels)
    if -1 in unique_clusters:
        unique_clusters.remove(-1)
        
    for cid in unique_clusters:
        cluster_df = df[df['cluster_id'] == cid]
        count = len(cluster_df)
        center_lat = float(cluster_df['latitude'].mean())
        center_lon = float(cluster_df['longitude'].mean())
        
        # Calculate maximum dispersion radius from centroid
        distances = [
            haversine_distance_km(center_lat, center_lon, row['latitude'], row['longitude'])
            for _, row in cluster_df.iterrows()
        ]
        max_dist_km = max(distances) if distances else 5.0
        dispersion_radius_km = max(round(max_dist_km + 8.0, 1), 12.0) # Add buffer zone
        
        # Pests and severity in cluster
        pests = cluster_df['pest_name'].value_counts().to_dict()
        top_pest = cluster_df['pest_name'].mode()[0]
        crops = cluster_df['crop_type'].unique().tolist()
        severe_count = len(cluster_df[cluster_df['severity'].isin(['High', 'Severe'])])
        
        # Compute Risk Index (0 - 100)
        risk_score = min(int((count * 10) + (severe_count * 15)), 98)
        if risk_score >= 75:
            risk_tier = "CRITICAL OUTBREAK"
            color_hex = "#D62828" # Red
        elif risk_score >= 50:
            risk_tier = "HIGH RISK CLUSTER"
            color_hex = "#F77F00" # Orange
        else:
            risk_tier = "MODERATE MONITORING"
            color_hex = "#FCBF49" # Amber
            
        hotspots_summary.append({
            "cluster_id": int(cid),
            "top_pest": top_pest,
            "report_count": count,
            "center_lat": round(center_lat, 5),
            "center_lon": round(center_lon, 5),
            "radius_km": dispersion_radius_km,
            "risk_score": risk_score,
            "risk_tier": risk_tier,
            "color_hex": color_hex,
            "crops_threatened": crops,
            "all_pests": pests,
            "location_name": cluster_df['location_name'].mode()[0] if not cluster_df['location_name'].empty else f"Zone #{cid+1}"
        })
        
    # Sort hotspots by highest risk
    hotspots_summary.sort(key=lambda x: x["risk_score"], reverse=True)
    
    return df.to_dict('records'), hotspots_summary

def assess_farm_vulnerability(farm_lat, farm_lon, farm_crop, hotspots_summary):
    """
    Evaluates risk for an individual farm based on proximity to active hotspots.
    Returns vulnerability profile, nearest distance, and preventive guidelines.
    """
    if not hotspots_summary:
        return {
            "threat_level": "LOW",
            "distance_km": None,
            "message": "No active clustered pest outbreaks detected within the regional monitoring zone.",
            "recommended_action": "Maintain routine crop scouting every 5–7 days."
        }
        
    closest_cluster = None
    min_distance = float('inf')
    
    for h in hotspots_summary:
        dist = haversine_distance_km(farm_lat, farm_lon, h['center_lat'], h['center_lon'])
        if dist < min_distance:
            min_distance = dist
            closest_cluster = h
            
    min_dist_rounded = round(min_distance, 1)
    
    # Check if inside cluster radius or buffer
    if min_distance <= closest_cluster['radius_km']:
        threat = "CRITICAL DIRECT THREAT"
        msg = f"Your farm is INSIDE the {closest_cluster['radius_km']} km active outbreak buffer for {closest_cluster['top_pest']} ({closest_cluster['location_name']})."
        actions = [
            f"Daily intensive scouting of all {farm_crop} fields at morning and twilight.",
            f"Erect pheromone / light traps immediately to gauge adult moth/insect influx.",
            "Inspect underside of young leaves for egg masses and early-instar larvae.",
            "Alert neighboring growers to synchronize community biological controls."
        ]
    elif min_distance <= closest_cluster['radius_km'] + 25.0:
        threat = "HIGH SURROUNDING RISK"
        msg = f"Active outbreak of {closest_cluster['top_pest']} located {min_dist_rounded} km away in {closest_cluster['location_name']}."
        actions = [
            "Increase scouting frequency to every 48 hours.",
            "Inspect field perimeter and border windbreaks.",
            "Prepare organic deterrents (e.g. neem oil spray) if wind trajectory favors pest dispersal."
        ]
    elif min_distance <= 80.0:
        threat = "MODERATE WATCH"
        msg = f"Nearest pest cluster ({closest_cluster['top_pest']}) is {min_dist_rounded} km distant."
        actions = [
            "Maintain twice-weekly scouting.",
            "Monitor regional agricultural extension advisories for weather-induced migration."
        ]
    else:
        threat = "LOW / SAFE PERIMETER"
        msg = f"Nearest documented pest cluster is {min_dist_rounded} km away."
        actions = ["Continue standard integrated pest management protocols."]
        
    return {
        "threat_level": threat,
        "nearest_cluster": closest_cluster,
        "distance_km": min_dist_rounded,
        "message": msg,
        "actions": actions
    }
