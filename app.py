"""RenalCare AI — Main Application Entry Point."""

import streamlit as st

st.set_page_config(
    page_title="RenalCare AI",
    page_icon="\U0001fac0",
    layout="wide",
    initial_sidebar_state="expanded",
)

from components.styles import inject_css
inject_css()

# ── Session defaults ───────────────────────────────────────────────────────
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"
if "risk_result" not in st.session_state:
    st.session_state.risk_result = None
if "med_result" not in st.session_state:
    st.session_state.med_result = None
if "econ_result" not in st.session_state:
    st.session_state.econ_result = None

# ── Navigation helper ──────────────────────────────────────────────────────
def go(page: str):
    st.session_state.current_page = page
    st.rerun()

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo block
    st.markdown("""
    <div style="padding:1.6rem 1.2rem 0.8rem 1.2rem;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
            <div style="width:38px;height:38px;background:linear-gradient(135deg,#14B8A6,#6366F1);
                        border-radius:10px;display:flex;align-items:center;justify-content:center;
                        font-size:1.15rem;flex-shrink:0;">\U0001fac0</div>
            <div>
                <div style="font-size:1.02rem;font-weight:800;color:#F1F5F9;
                            letter-spacing:-0.01em;line-height:1.2;">RenalCare AI</div>
                <div style="font-size:0.65rem;color:#64748B;font-weight:500;
                            letter-spacing:0.06em;text-transform:uppercase;">Clinical Intelligence</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Version + role badges
    st.markdown("""
    <div style="padding:0 1.2rem 1rem 1.2rem;display:flex;gap:6px;flex-wrap:wrap;">
        <span style="background:rgba(20,184,166,0.15);color:#14B8A6;font-size:0.65rem;
                     font-weight:700;padding:3px 8px;border-radius:20px;letter-spacing:0.05em;">
            v1.0
        </span>
        <span style="background:rgba(99,102,241,0.15);color:#818CF8;font-size:0.65rem;
                     font-weight:700;padding:3px 8px;border-radius:20px;letter-spacing:0.05em;">
            PharmD Edition
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:0 1.2rem 0.8rem 1.2rem;">', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 1.2rem 0.3rem;font-size:0.65rem;font-weight:700;color:#475569;letter-spacing:0.1em;text-transform:uppercase;">Navigation</div>', unsafe_allow_html=True)

    nav_items = [
        ("Home",       "\U0001f3e0",  "Home"),
        ("Risk",       "❤️", "Kidney Risk Assessment"),
        ("Evidence",   "\U0001f50d",  "Clinical Evidence"),
        ("Medication", "\U0001f48a",  "Medication Intelligence"),
        ("Nutrition",  "\U0001f966",  "Nutrition Intelligence"),
        ("Economics",  "\U0001f4ca",  "Pharmacoeconomics"),
        ("Report",     "\U0001f4c4",  "Report Generator"),
    ]

    for key, icon, label in nav_items:
        if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
            go(key)

    # Future modules lock block
    st.markdown("""
    <div style="margin:1.2rem 0.8rem 0;border-radius:10px;
                background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);
                padding:0.9rem 1rem;">
        <div style="font-size:0.65rem;font-weight:700;color:#475569;letter-spacing:0.1em;
                    text-transform:uppercase;margin-bottom:0.5rem;">Future Modules</div>
        <div style="display:flex;flex-direction:column;gap:4px;">
            <div style="font-size:0.78rem;color:#334155;">\U0001f512 Transplant Eligibility</div>
            <div style="font-size:0.78rem;color:#334155;">\U0001f512 Fluid Management</div>
            <div style="font-size:0.78rem;color:#334155;">\U0001f512 Anemia Protocol</div>
            <div style="font-size:0.78rem;color:#334155;">\U0001f512 Patient Outcome ML</div>
        </div>
        <div style="margin-top:0.6rem;padding-top:0.5rem;border-top:1px solid rgba(255,255,255,0.05);
                    font-size:0.69rem;color:#475569;">V2 Roadmap &bull; 2025</div>
    </div>
    """, unsafe_allow_html=True)

    # Bottom user card
    st.markdown("""
    <div style="margin-top:2rem;padding:0.9rem 1.2rem;border-top:1px solid rgba(255,255,255,0.06);
                background:rgba(0,0,0,0.12);">
        <div style="display:flex;align-items:center;gap:8px;">
            <div style="width:30px;height:30px;background:linear-gradient(135deg,#1E3A5F,#6366F1);
                        border-radius:50%;display:flex;align-items:center;justify-content:center;
                        font-size:0.75rem;font-weight:700;color:white;flex-shrink:0;">RH</div>
            <div>
                <div style="font-size:0.77rem;font-weight:600;color:#E2E8F0;">Reema Hussain</div>
                <div style="font-size:0.67rem;color:#64748B;">PharmD &bull; Researcher</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Router ─────────────────────────────────────────────────────────────────
page = st.session_state.current_page

if page == "Home":
    from pages.home import render; render()
elif page == "Risk":
    from pages.kidney_risk import render; render()
elif page == "Evidence":
    from pages.clinical_evidence import render; render()
elif page == "Medication":
    from pages.medication_intelligence import render; render()
elif page == "Nutrition":
    from pages.nutrition_intelligence import render; render()
elif page == "Economics":
    from pages.pharmacoeconomics import render; render()
elif page == "Report":
    from pages.report_generator import render; render()
