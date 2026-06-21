"""Global CSS Design System for RenalCare AI."""

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ══════════════════════════════════════════
   ROOT VARIABLES
══════════════════════════════════════════ */
:root {
    --primary:        #1E3A5F;
    --primary-light:  #2563EB;
    --teal:           #14B8A6;
    --teal-light:     #CCFBF1;
    --purple:         #6366F1;
    --purple-light:   #EEF2FF;
    --bg:             #F8FAFC;
    --white:          #FFFFFF;
    --text:           #0F172A;
    --text-secondary: #64748B;
    --text-muted:     #94A3B8;
    --success:        #10B981;
    --success-light:  #D1FAE5;
    --warning:        #F59E0B;
    --warning-light:  #FEF3C7;
    --danger:         #EF4444;
    --danger-light:   #FEE2E2;
    --border:         #E2E8F0;
    --border-light:   #F1F5F9;
    --shadow-sm:  0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow:     0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
    --shadow-md:  0 8px 16px -4px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.04);
    --shadow-lg:  0 20px 25px -5px rgba(0,0,0,0.08), 0 8px 10px -6px rgba(0,0,0,0.04);
    --radius-sm:  6px;
    --radius:     10px;
    --radius-lg:  16px;
    --radius-xl:  24px;
}

/* ══════════════════════════════════════════
   RESET & BASE
══════════════════════════════════════════ */
* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text);
    -webkit-font-smoothing: antialiased;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stDecoration"] { display: none; }
div[data-testid="stToolbar"] { display: none; }

/* Main content area */
.main .block-container {
    background: var(--bg);
    padding: 1.5rem 2rem 3rem 2rem;
    max-width: 1400px;
}

/* ══════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F1F3D 0%, #1E3A5F 45%, #0D2137 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0;
}
[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    color: #94A3B8 !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    padding: 0.55rem 1rem !important;
    border-radius: 8px !important;
    text-align: left !important;
    width: 100% !important;
    transition: all 0.18s ease !important;
    margin: 1px 0 !important;
    letter-spacing: 0.01em !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.09) !important;
    color: #FFFFFF !important;
    transform: translateX(2px) !important;
}

/* ══════════════════════════════════════════
   CARD SYSTEM
══════════════════════════════════════════ */
.rc-card {
    background: var(--white);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    box-shadow: var(--shadow);
    border: 1px solid var(--border-light);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.rc-card:hover { box-shadow: var(--shadow-md); }

.rc-card-sm {
    background: var(--white);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-light);
}

/* ══════════════════════════════════════════
   KPI METRIC CARDS
══════════════════════════════════════════ */
.kpi-card {
    background: var(--white);
    border-radius: var(--radius-lg);
    padding: 1.4rem 1.5rem;
    box-shadow: var(--shadow);
    border: 1px solid var(--border-light);
    position: relative;
    overflow: hidden;
    transition: all 0.22s ease;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--teal), var(--purple));
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
}
.kpi-icon {
    width: 44px; height: 44px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    margin-bottom: 0.8rem;
}
.kpi-value {
    font-size: 2rem;
    font-weight: 800;
    color: var(--text);
    line-height: 1;
    margin-bottom: 0.3rem;
    letter-spacing: -0.03em;
}
.kpi-label {
    font-size: 0.78rem;
    color: var(--text-secondary);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ══════════════════════════════════════════
   MODULE FEATURE CARDS
══════════════════════════════════════════ */
.module-card {
    background: var(--white);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    box-shadow: var(--shadow);
    border: 1px solid var(--border-light);
    height: 100%;
    transition: all 0.22s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}
.module-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 0;
    background: linear-gradient(135deg, rgba(20,184,166,0.05), rgba(99,102,241,0.05));
    transition: height 0.22s ease;
}
.module-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
    border-color: rgba(20,184,166,0.3);
}
.module-card:hover::after { height: 100%; }
.module-icon {
    width: 52px; height: 52px;
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem;
    margin-bottom: 1rem;
}
.module-title {
    font-size: 0.97rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 0.4rem;
}
.module-desc {
    font-size: 0.8rem;
    color: var(--text-secondary);
    line-height: 1.55;
    margin-bottom: 1rem;
}

/* ══════════════════════════════════════════
   BADGES & PILLS
══════════════════════════════════════════ */
.badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.badge-low      { background: var(--success-light); color: #065F46; }
.badge-moderate { background: var(--warning-light); color: #92400E; }
.badge-high     { background: #FEE2E2; color: #991B1B; }
.badge-critical { background: #F3E8FF; color: #6B21A8; }
.badge-info     { background: #EFF6FF; color: #1D4ED8; }
.badge-teal     { background: var(--teal-light); color: #0F766E; }
.badge-purple   { background: var(--purple-light); color: #4338CA; }

/* ══════════════════════════════════════════
   SECTION HEADERS
══════════════════════════════════════════ */
.section-title {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    padding-bottom: 0.6rem;
    border-bottom: 2px solid var(--border-light);
}
.section-title-accent {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--primary);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.8rem;
}

/* ══════════════════════════════════════════
   PAGE HEADERS
══════════════════════════════════════════ */
.page-header {
    background: linear-gradient(135deg, var(--primary) 0%, #2563EB 60%, var(--teal) 100%);
    border-radius: var(--radius-xl);
    padding: 2rem 2.5rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
}
.page-header::after {
    content: '';
    position: absolute;
    bottom: -60px; right: 60px;
    width: 250px; height: 250px;
    background: rgba(255,255,255,0.03);
    border-radius: 50%;
}
.page-header h1 {
    color: white !important;
    font-size: 1.6rem !important;
    font-weight: 800 !important;
    margin: 0 0 0.3rem 0 !important;
    letter-spacing: -0.02em;
}
.page-header p {
    color: rgba(255,255,255,0.75) !important;
    font-size: 0.88rem !important;
    margin: 0 !important;
}

/* ══════════════════════════════════════════
   ALERT / INFO BOXES
══════════════════════════════════════════ */
.alert {
    border-radius: var(--radius);
    padding: 0.85rem 1.1rem;
    font-size: 0.85rem;
    line-height: 1.55;
    margin: 0.5rem 0;
    display: flex;
    gap: 0.6rem;
    align-items: flex-start;
}
.alert-info    { background: #EFF6FF; border-left: 3px solid #3B82F6; color: #1E40AF; }
.alert-success { background: var(--success-light); border-left: 3px solid var(--success); color: #065F46; }
.alert-warning { background: var(--warning-light); border-left: 3px solid var(--warning); color: #92400E; }
.alert-danger  { background: var(--danger-light); border-left: 3px solid var(--danger); color: #991B1B; }
.alert-purple  { background: var(--purple-light); border-left: 3px solid var(--purple); color: #3730A3; }

/* ══════════════════════════════════════════
   FLAG CARDS (Medication)
══════════════════════════════════════════ */
.flag-card {
    background: var(--white);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-light);
    border-left-width: 4px;
    transition: all 0.18s ease;
}
.flag-card:hover { box-shadow: var(--shadow); }
.flag-high     { border-left-color: var(--danger); }
.flag-moderate { border-left-color: var(--warning); }
.flag-low      { border-left-color: #3B82F6; }

/* ══════════════════════════════════════════
   NUTRIENT BARS
══════════════════════════════════════════ */
.nutrient-row {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.8rem;
}
.nutrient-label { font-size: 0.82rem; font-weight: 600; color: var(--text-secondary); min-width: 80px; }
.nutrient-bar-bg { flex: 1; background: var(--border-light); border-radius: 999px; height: 7px; }
.nutrient-bar-fill { height: 7px; border-radius: 999px; transition: width 0.4s ease; }
.nutrient-value { font-size: 0.8rem; font-weight: 600; color: var(--text); min-width: 70px; text-align: right; }

/* ══════════════════════════════════════════
   SUITABILITY INDICATORS
══════════════════════════════════════════ */
.suit-safe    { background:#F0FDF4; border:2px solid #86EFAC; border-radius:var(--radius-lg); padding:1.2rem; }
.suit-caution { background:#FFFBEB; border:2px solid #FCD34D; border-radius:var(--radius-lg); padding:1.2rem; }
.suit-avoid   { background:#FFF1F2; border:2px solid #FDA4AF; border-radius:var(--radius-lg); padding:1.2rem; }

/* ══════════════════════════════════════════
   FORM STYLING
══════════════════════════════════════════ */
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stNumberInput > div > div > input,
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 8px !important;
    border-color: var(--border) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.87rem !important;
}
.stSelectbox > div > div:focus-within,
.stTextInput > div > div:focus-within,
.stTextArea > div > div:focus-within {
    border-color: var(--teal) !important;
    box-shadow: 0 0 0 3px rgba(20,184,166,0.1) !important;
}

/* ══════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, var(--primary), #2563EB) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.4rem !important;
    font-weight: 600 !important;
    font-size: 0.87rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(30,58,95,0.25) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(30,58,95,0.35) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ══════════════════════════════════════════
   TABS
══════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: var(--border-light);
    border-radius: 10px;
    padding: 4px;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px;
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--text-secondary) !important;
    background: transparent;
    padding: 0.45rem 1rem;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: var(--primary) !important;
    font-weight: 600 !important;
    box-shadow: var(--shadow-sm) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.2rem; }

/* ══════════════════════════════════════════
   EXPANDER
══════════════════════════════════════════ */
.streamlit-expanderHeader {
    background: var(--border-light) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    color: var(--text) !important;
}

/* ══════════════════════════════════════════
   PROGRESS BAR
══════════════════════════════════════════ */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--teal), var(--purple)) !important;
    border-radius: 999px !important;
}

/* ══════════════════════════════════════════
   DIVIDER
══════════════════════════════════════════ */
hr { border: none; border-top: 1px solid var(--border-light); margin: 1.2rem 0; }

/* ══════════════════════════════════════════
   SCROLLBAR
══════════════════════════════════════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94A3B8; }

/* ══════════════════════════════════════════
   UTILITY CLASSES
══════════════════════════════════════════ */
.flex-between { display:flex; justify-content:space-between; align-items:center; }
.flex-center  { display:flex; justify-content:center; align-items:center; }
.flex-gap     { display:flex; align-items:center; gap:0.6rem; }
.text-primary { color: var(--primary) !important; }
.text-teal    { color: var(--teal) !important; }
.text-muted   { color: var(--text-muted) !important; }
.text-sm      { font-size: 0.82rem !important; }
.text-xs      { font-size: 0.73rem !important; }
.fw-700       { font-weight: 700 !important; }
.fw-600       { font-weight: 600 !important; }
.mt-1         { margin-top: 0.5rem !important; }
.mt-2         { margin-top: 1rem !important; }
.mb-1         { margin-bottom: 0.5rem !important; }
.gap-sm       { gap: 0.4rem; }

/* ══════════════════════════════════════════
   GLASSMORPHISM HERO
══════════════════════════════════════════ */
.glass-card {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: var(--radius-lg);
    padding: 1rem 1.5rem;
}

/* ══════════════════════════════════════════
   TABLE STYLES
══════════════════════════════════════════ */
.rc-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.84rem;
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}
.rc-table thead tr { background: var(--primary); color: white; }
.rc-table thead th { padding: 10px 14px; text-align: left; font-weight: 600; font-size: 0.79rem; letter-spacing: 0.04em; }
.rc-table tbody tr { border-bottom: 1px solid var(--border-light); transition: background 0.15s; }
.rc-table tbody tr:hover { background: var(--bg); }
.rc-table tbody tr:last-child { border-bottom: none; }
.rc-table tbody td { padding: 9px 14px; color: var(--text); vertical-align: middle; }
.rc-table tbody tr:nth-child(even) { background: var(--border-light); }

/* ══════════════════════════════════════════
   ANIMATED GRADIENT TEXT
══════════════════════════════════════════ */
.gradient-text {
    background: linear-gradient(135deg, var(--teal), var(--purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ══════════════════════════════════════════
   SIDEBAR NAV OVERRIDE
══════════════════════════════════════════ */
div[data-testid="stSidebarNav"] { display: none !important; }
</style>
"""


def inject_css():
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
