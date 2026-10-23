"""
CropGuardian AI - UI Styling & Agricultural Theme
Agricultural green, warm cream, terracotta, and earthy neutral palette.
Custom CSS components for high-contrast cards, badges, and mobile responsiveness.
"""

import streamlit as st

def apply_agricultural_theme():
    """Injects responsive agricultural styling and theme variables into Streamlit."""
    custom_css = """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

    :root {
        --primary-forest: #1E4620;
        --secondary-emerald: #2D6A4F;
        --sage-green: #52796F;
        --earth-amber: #DDA15E;
        --terracotta: #C16643;
        --danger-red: #D62828;
        --cream-bg: #FDFBF7;
        --surface-white: #FFFFFF;
        --border-subtle: #E8E4DC;
        --text-dark: #1F2937;
        --text-muted: #6B7280;
    }

    /* Overall Layout Adjustments */
    .stApp {
        background-color: var(--cream-bg);
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: var(--text-dark);
    }

    /* Header Banner */
    .agri-banner {
        background: linear-gradient(135deg, #1E4620 0%, #2D6A4F 60%, #354F52 100%);
        border-radius: 16px;
        padding: 28px 32px;
        color: #FFFFFF;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(30, 70, 32, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    .agri-banner h1 {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        color: #FFFFFF !important;
        letter-spacing: -0.5px;
    }
    .agri-banner p {
        color: #E2E8F0;
        font-size: 1.05rem;
        margin-top: 8px;
        margin-bottom: 0;
        max-width: 720px;
    }

    /* Cards */
    .agri-card {
        background: var(--surface-white);
        border-radius: 14px;
        border: 1px solid var(--border-subtle);
        padding: 22px 24px;
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .agri-card:hover {
        box-shadow: 0 8px 24px rgba(30, 70, 32, 0.08);
    }

    /* Card Titles */
    .agri-card-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--primary-forest);
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-critical {
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1px solid #F87171;
    }
    .badge-warning {
        background-color: #FEF3C7;
        color: #92400E;
        border: 1px solid #FCD34D;
    }
    .badge-safe {
        background-color: #DCFCE7;
        color: #166534;
        border: 1px solid #86EFAC;
    }
    .badge-simulated {
        background-color: #EDE9FE;
        color: #5B21B6;
        border: 1px solid #C4B5FD;
    }
    .badge-real {
        background-color: #E0F2FE;
        color: #075985;
        border: 1px solid #7DD3FC;
    }

    /* Metric Boxes */
    .metric-container {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
        margin-bottom: 20px;
    }
    .metric-box {
        flex: 1;
        min-width: 140px;
        background: #FFFFFF;
        border-radius: 12px;
        border: 1px solid var(--border-subtle);
        padding: 16px 20px;
        border-left: 5px solid var(--secondary-emerald);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: var(--primary-forest);
        font-family: 'Space Grotesk', sans-serif;
        line-height: 1.1;
    }
    .metric-label {
        font-size: 0.85rem;
        color: var(--text-muted);
        font-weight: 600;
        margin-top: 4px;
        text-transform: uppercase;
    }

    /* Disclaimer Notice */
    .disclaimer-box {
        background-color: #FFFBEB;
        border-left: 4px solid #F59E0B;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 14px 0;
        color: #78350F;
        font-size: 0.9rem;
    }
    
    .privacy-box {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 14px 0;
        color: #1E3A8A;
        font-size: 0.9rem;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .agri-banner {
            padding: 20px;
        }
        .agri-banner h1 {
            font-size: 1.6rem;
        }
        .metric-box {
            min-width: 100%;
        }
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
