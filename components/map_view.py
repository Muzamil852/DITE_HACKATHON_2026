"""
CropGuardian AI - Interactive Geospatial Outbreak Heatmap
Renders high-impact interactive maps using Plotly & Pydeck,
visualizing DBSCAN outbreak clusters, individual reports, and risk buffer zones.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

def render_pest_outbreak_map(reports, hotspots, user_farm_lat=None, user_farm_lon=None, basemap_style="carto-positron"):
    """
    Renders an interactive geospatial map with multiple layers:
    - Active Outbreak Hotspots (DBSCAN Clusters with radius buffers)
    - Real Farmer Field Reports (Distinctive Markers)
    - Simulated Baseline Demonstration Reports (Clearly Labeled)
    - User's Monitored Farm Location
    """
    if not reports:
        st.info("No pest observation data available to map.")
        return
        
    df = pd.DataFrame(reports)
    
    # Calculate map center
    center_lat = float(df['latitude'].mean())
    center_lon = float(df['longitude'].mean())
    
    fig = go.Figure()
    
    # 1. LAYER: DBSCAN Hotspot Risk Perimeters (Cluster Centroids & Risk Radii)
    if hotspots:
        hotspots_df = pd.DataFrame(hotspots)
        
        # Add outer translucent threat buffers
        for h in hotspots:
            # Approximate circle buffer on mapbox
            fig.add_trace(go.Scattermapbox(
                lat=[h['center_lat']],
                lon=[h['center_lon']],
                mode='markers+text',
                marker=dict(
                    size=max(int(h['radius_km'] * 2.2), 35),
                    color=h['color_hex'],
                    opacity=0.28
                ),
                text=[f"⚡ {h['risk_tier']}"],
                textposition="top center",
                textfont=dict(size=12, color=h['color_hex'], family="Space Grotesk"),
                hoverinfo='text',
                hovertext=(
                    f"<b>EPICENTER: {h['location_name']}</b><br>"
                    f"<b>Threat Tier:</b> {h['risk_tier']} (Score: {h['risk_score']}/100)<br>"
                    f"<b>Primary Pest:</b> {h['top_pest']}<br>"
                    f"<b>Cluster Radius:</b> {h['radius_km']} km<br>"
                    f"<b>Crops Affected:</b> {', '.join(h['crops_threatened'])}<br>"
                    f"<b>Scouted Reports:</b> {h['report_count']} incidents"
                ),
                name=f"Hotspot: {h['location_name']}",
                showlegend=True
            ))
            
            # Hotspot Core Center
            fig.add_trace(go.Scattermapbox(
                lat=[h['center_lat']],
                lon=[h['center_lon']],
                mode='markers',
                marker=dict(
                    size=16,
                    color=h['color_hex'],
                    opacity=0.95
                ),
                hoverinfo='skip',
                showlegend=False
            ))

    # 2. LAYER: Farmer Submitted Real Reports
    real_reports = df[df['is_simulated'] == 0]
    if not real_reports.empty:
        hover_texts_real = [
            f"<b>🚜 FARMER REPORT #{r['id']}</b><br>"
            f"<b>Pest:</b> {r['pest_name']}<br>"
            f"<b>Crop:</b> {r['crop_type']}<br>"
            f"<b>Severity:</b> {r['severity']}<br>"
            f"<b>Date:</b> {r['timestamp']}<br>"
            f"<b>Status:</b> {r['verification_status']}<br>"
            f"<b>Notes:</b> {r.get('notes', 'None')}"
            for _, r in real_reports.iterrows()
        ]
        
        fig.add_trace(go.Scattermapbox(
            lat=real_reports['latitude'],
            lon=real_reports['longitude'],
            mode='markers',
            marker=dict(
                size=14,
                color='#00F5D4', # Bright Cyber Mint / Cyan
                opacity=0.95
            ),
            hoverinfo='text',
            hovertext=hover_texts_real,
            name="🚜 Farmer Reports (Live Observed)",
            showlegend=True
        ))

    # 3. LAYER: Baseline Demonstration Reports (Clearly Labeled Simulated)
    sim_reports = df[df['is_simulated'] == 1]
    if not sim_reports.empty:
        severity_colors = {
            'Severe': '#9D0208',
            'High': '#D00000',
            'Medium': '#F48C06',
            'Low': '#FFBA08'
        }
        marker_colors = [severity_colors.get(s, '#FAA307') for s in sim_reports['severity']]
        
        hover_texts_sim = [
            f"<b>🔬 DEMO SCOUTING REPORT #{r['id']}</b><br>"
            f"<b>Pest:</b> {r['pest_name']}<br>"
            f"<b>Crop:</b> {r['crop_type']}<br>"
            f"<b>Severity:</b> {r['severity']}<br>"
            f"<b>Location:</b> {r['location_name']}<br>"
            f"<b>Timestamp:</b> {r['timestamp']}<br>"
            f"<i>[SIMULATED BASELINE FOR DEMONSTRATION]</i>"
            for _, r in sim_reports.iterrows()
        ]
        
        fig.add_trace(go.Scattermapbox(
            lat=sim_reports['latitude'],
            lon=sim_reports['longitude'],
            mode='markers',
            marker=dict(
                size=9,
                color=marker_colors,
                opacity=0.8
            ),
            hoverinfo='text',
            hovertext=hover_texts_sim,
            name="🔬 Demonstration Baseline Reports",
            showlegend=True
        ))
        
    # 4. LAYER: User Monitored Farm (if provided)
    if user_farm_lat is not None and user_farm_lon is not None:
        fig.add_trace(go.Scattermapbox(
            lat=[user_farm_lat],
            lon=[user_farm_lon],
            mode='markers+text',
            marker=dict(
                size=18,
                color='#3A86FF', # Bright Blue
                opacity=1.0
            ),
            text=["📍 Your Monitored Farm"],
            textposition="bottom right",
            textfont=dict(size=13, color='#1E3A8A', family="Space Grotesk"),
            hoverinfo='text',
            hovertext=f"<b>📍 Your Monitored Farm</b><br>Lat: {user_farm_lat:.4f}, Lon: {user_farm_lon:.4f}",
            name="📍 Your Monitored Farm",
            showlegend=True
        ))

    fig.update_layout(
        mapbox=dict(
            style=basemap_style,
            center=dict(lat=center_lat, lon=center_lon),
            zoom=6.8
        ),
        margin=dict(l=0, r=0, t=20, b=0),
        height=580,
        legend=dict(
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.02,
            bgcolor="rgba(255, 255, 255, 0.92)",
            bordercolor="#CBD5E1",
            borderwidth=1,
            font=dict(size=11, family="Plus Jakarta Sans")
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
