"""
RenalCare AI — Main Application Entry Point
AI-Powered Kidney Disease Intelligence Platform
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

st.set_page_config(
    page_title="RenalCare AI",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "RenalCare AI v1.0 — AI-Powered Kidney Disease Intelligence Platform",
        "Report a bug": None,
        "Get Help": None,
    },
)

# ---- Global CSS ----
st.markdown("""
<style>
/* ── Import font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e3a5f 0%, #2c5282 60%, #1a365d 100%);
    border-right: none;
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] .stRadio > label {
    color: #90cdf4 !important;
    font-weight: 600;
}

/* ── Main background ── */
.main .block-container {
    background-color: #f7fafc;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

/* ── Metric cards ── */
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    border-left: 4px solid #2980b9;
    margin-bottom: 0.5rem;
}
.metric-card h3 {
    font-size: 2rem;
    font-weight: 700;
    color: #1e3a5f;
    margin: 0;
}
.metric-card p {
    font-size: 0.8rem;
    color: #718096;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── Section headers ── */
.section-header {
    background: linear-gradient(135deg, #1e3a5f 0%, #2980b9 100%);
    color: white !important;
    padding: 0.8rem 1.2rem;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 1rem;
}

/* ── Risk badges ── */
.badge-low    { background:#d5f5e3; color:#1e8449; padding:4px 12px; border-radius:20px; font-weight:600; font-size:0.85rem; }
.badge-mod    { background:#fef9e7; color:#d35400; padding:4px 12px; border-radius:20px; font-weight:600; font-size:0.85rem; }
.badge-high   { background:#fdf2e9; color:#e74c3c; padding:4px 12px; border-radius:20px; font-weight:600; font-size:0.85rem; }
.badge-crit   { background:#fdedec; color:#c0392b; padding:4px 12px; border-radius:20px; font-weight:600; font-size:0.85rem; }

/* ── Info box ── */
.info-box {
    background: #ebf8ff;
    border: 1px solid #bee3f8;
    border-left: 4px solid #3182ce;
    border-radius: 6px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.88rem;
}
.warning-box {
    background: #fffaf0;
    border: 1px solid #fbd38d;
    border-left: 4px solid #ed8936;
    border-radius: 6px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.88rem;
}
.danger-box {
    background: #fff5f5;
    border: 1px solid #fed7d7;
    border-left: 4px solid #e53e3e;
    border-radius: 6px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.88rem;
}
.success-box {
    background: #f0fff4;
    border: 1px solid #c6f6d5;
    border-left: 4px solid #38a169;
    border-radius: 6px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.88rem;
}

/* ── Nutrition suitability ── */
.food-safe   { background:#f0fff4; border:2px solid #38a169; border-radius:10px; padding:1rem; }
.food-caution{ background:#fffff0; border:2px solid #d69e2e; border-radius:10px; padding:1rem; }
.food-avoid  { background:#fff5f5; border:2px solid #e53e3e; border-radius:10px; padding:1rem; }

/* ── Sidebar nav pills ── */
div[data-testid="stSidebarNav"] {display: none;}

/* ── Tables ── */
.dataframe { font-size: 0.85rem !important; }

/* ── Progress bar colour ── */
.stProgress > div > div > div > div { background: linear-gradient(90deg, #2980b9, #16a085); }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #1e3a5f, #2980b9);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    font-weight: 600;
    transition: all 0.2s;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(41,128,185,0.4);
}
</style>
""", unsafe_allow_html=True)


# ---- Sidebar ----
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1.5rem 0 1rem 0;'>
        <div style='font-size:2.5rem;'>🫀</div>
        <div style='font-size:1.3rem; font-weight:700; color:white; letter-spacing:0.05em;'>RenalCare AI</div>
        <div style='font-size:0.72rem; color:#90cdf4; margin-top:4px;'>AI-Powered Kidney Intelligence</div>
        <div style='background:rgba(255,255,255,0.1); border-radius:6px; padding:3px 10px; margin-top:8px; display:inline-block;'>
            <span style='font-size:0.7rem; color:#a0d8ef;'>v1.0 — Clinical Preview</span>
        </div>
    </div>
    <hr style='border-color:rgba(255,255,255,0.15); margin: 0.5rem 0 1rem 0;'>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:0.7rem; color:#90cdf4; font-weight:600; letter-spacing:0.1em; padding:0 0.5rem 0.3rem;'>NAVIGATION</div>", unsafe_allow_html=True)

    pages = {
        "🏠  Dashboard": "Home",
        "🫀  Kidney Risk Assessment": "Risk",
        "🔬  Clinical Evidence": "Evidence",
        "💊  Medication Intelligence": "Medication",
        "🥗  Nutrition Intelligence": "Nutrition",
        "💰  Pharmacoeconomics": "Economics",
        "📋  Report Generator": "Report",
    }

    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    for label, key in pages.items():
        active = st.session_state.current_page == key
        btn_style = "background:rgba(255,255,255,0.18); border-radius:8px;" if active else ""
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.current_page = key

    st.markdown("""
    <hr style='border-color:rgba(255,255,255,0.15); margin: 1rem 0 0.5rem 0;'>
    <div style='padding: 0 0.5rem;'>
        <div style='font-size:0.7rem; color:#90cdf4; font-weight:600; letter-spacing:0.1em; margin-bottom:0.5rem;'>FUTURE MODULES</div>
        <div style='font-size:0.78rem; color:rgba(255,255,255,0.4); line-height:1.8;'>
            🔮 CKD Progression AI <span style='font-size:0.65rem; background:rgba(255,255,255,0.1); border-radius:4px; padding:1px 5px;'>V2</span><br>
            📊 Adherence Intelligence <span style='font-size:0.65rem; background:rgba(255,255,255,0.1); border-radius:4px; padding:1px 5px;'>V2</span><br>
            🧬 Kidney Digital Twin <span style='font-size:0.65rem; background:rgba(255,255,255,0.1); border-radius:4px; padding:1px 5px;'>V3</span><br>
            🌍 Population Health <span style='font-size:0.65rem; background:rgba(255,255,255,0.1); border-radius:4px; padding:1px 5px;'>V3</span><br>
            🏥 Hospital Integration <span style='font-size:0.65rem; background:rgba(255,255,255,0.1); border-radius:4px; padding:1px 5px;'>V3</span>
        </div>
    </div>
    <hr style='border-color:rgba(255,255,255,0.15); margin: 1rem 0 0.5rem 0;'>
    <div style='text-align:center; font-size:0.68rem; color:rgba(255,255,255,0.3);'>
        © 2025 RenalCare AI<br>Clinical Decision Support Only
    </div>
    """, unsafe_allow_html=True)

# ---- Page routing ----
page = st.session_state.current_page

if page == "Home":
    from pages.home import render
    render()
elif page == "Risk":
    from pages.kidney_risk import render
    render()
elif page == "Evidence":
    from pages.clinical_evidence import render
    render()
elif page == "Medication":
    from pages.medication_intelligence import render
    render()
elif page == "Nutrition":
    from pages.nutrition_intelligence import render
    render()
elif page == "Economics":
    from pages.pharmacoeconomics import render
    render()
elif page == "Report":
    from pages.report_generator import render
    render()
