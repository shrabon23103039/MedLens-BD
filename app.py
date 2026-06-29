import streamlit as st
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.db import init_db, seed_drugs
from utils.outbreak import init_outbreak_db

# Initialize databases on startup
init_db()
seed_drugs()
init_outbreak_db()

# Page config
st.set_page_config(
    page_title="MedLens BD 🩺",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8f5f3 100%);
    }
    
    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #00897B, #00695C);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 0.5rem;
        box-shadow: 0 4px 20px rgba(0,137,123,0.3);
    }
    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        font-size: 1rem;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
    }
    
    /* Stats bar */
    .stats-bar {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        flex: 1;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-top: 3px solid #00897B;
    }
    .stat-number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #00897B;
    }
    .stat-label {
        font-size: 0.75rem;
        color: #888;
        margin-top: 0.2rem;
    }
    
    /* Medicine card */
    .medicine-card {
        background: white;
        border-left: 4px solid #00897B;
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: transform 0.2s;
    }
    .medicine-card:hover {
        transform: translateX(4px);
    }
    .medicine-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1A1A2E;
        margin-bottom: 0.5rem;
    }
    .medicine-detail {
        font-size: 0.9rem;
        color: #555;
        margin: 0.2rem 0;
    }
    .savings-badge {
        background: #E8F5E9;
        color: #2E7D32;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 0.5rem;
    }
    
    /* Warning box */
    .warning-box {
        background: linear-gradient(135deg, #FFF8E1, #FFF3E0);
        border-left: 4px solid #FF8F00;
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        box-shadow: 0 2px 8px rgba(255,143,0,0.1);
    }
    
    /* Danger box */
    .danger-box {
        background: linear-gradient(135deg, #FFEBEE, #FCE4EC);
        border-left: 4px solid #D32F2F;
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        box-shadow: 0 2px 8px rgba(211,47,47,0.1);
    }
    
    /* Success box */
    .success-box {
        background: linear-gradient(135deg, #E8F5E9, #F1F8E9);
        border-left: 4px solid #2E7D32;
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        box-shadow: 0 2px 8px rgba(46,125,50,0.1);
    }
    
    /* Info box */
    .info-box {
        background: linear-gradient(135deg, #E3F2FD, #E8EAF6);
        border-left: 4px solid #1565C0;
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin: 0.8rem 0;
    }
    
    /* Section header */
    .section-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #00695C;
        padding: 0.5rem 0;
        border-bottom: 2px solid #E0F2F1;
        margin: 1.5rem 0 1rem 0;
    }
    
    /* Upload area */
    .stFileUploader {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00897B, #00695C);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        width: 100%;
        box-shadow: 0 4px 12px rgba(0,137,123,0.3);
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,137,123,0.4);
    }
    
    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #00695C 0%, #004D40 100%);
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: white !important;
        font-weight: 500;
    }
    
    /* Divider */
    hr {
        border: none;
        border-top: 2px solid #E0F2F1;
        margin: 1.5rem 0;
    }
</style>
""", unsafe_allow_html=True)
# Header
st.markdown('<div class="main-header">🩺 MedLens BD</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-powered medical document understanding for every Bangladeshi patient</div>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.image("https://img.icons8.com/color/96/stethoscope.png", width=80)
st.sidebar.title("MedLens BD")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    [
        "💊 Prescription Explainer",
        "🧪 Lab Report Explainer",
        "🔍 Counterfeit Detector",
        "🗺️ Outbreak Map"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Language / ভাষা")
language = st.sidebar.radio("", ["English", "বাংলা"])

st.sidebar.markdown("---")
st.sidebar.markdown("""
<small>
⚠️ **Disclaimer**  
এটি শুধু তথ্যমূলক।  
ডাক্তারের পরামর্শ প্রতিস্থাপন নয়।  
*For informational use only.*
</small>
""", unsafe_allow_html=True)

# Route to pages
if page == "💊 Prescription Explainer":
    from pages.prescription import show
    show(language)

elif page == "🧪 Lab Report Explainer":
    from pages.lab_report import show
    show(language)

elif page == "🔍 Counterfeit Detector":
    from pages.counterfeit import show
    show(language)

elif page == "🗺️ Outbreak Map":
    from pages.outbreak_map import show
    show(language)