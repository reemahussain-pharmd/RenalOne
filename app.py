"""RenalCare AI — Main Application Entry Point."""

import streamlit as st

st.set_page_config(
    page_title="RenalCare AI",
    page_icon="\U0001fac0",
    layout="wide",
    initial_sidebar_state="expanded",
)

from components.styles import inject_css, sh
inject_css()

# ── Session defaults ───────────────────────────────────────────────────────
if "current_page"     not in st.session_state: st.session_state.current_page     = "Home"
if "risk_result"      not in st.session_state: st.session_state.risk_result      = None
if "med_result"       not in st.session_state: st.session_state.med_result       = None
if "econ_result"      not in st.session_state: st.session_state.econ_result      = None
if "nutrition_result" not in st.session_state: st.session_state.nutrition_result = None
if "adherence_result" not in st.session_state: st.session_state.adherence_result = None
if "patient_profile"  not in st.session_state: st.session_state.patient_profile  = None

# ── Navigation helper ──────────────────────────────────────────────────────
def go(page: str):
    st.session_state.current_page = page
    st.rerun()

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo block
    sh("""
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
    """)

    # Version + role badges
    sh("""
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
    """)

    sh('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:0 1.2rem 0.8rem 1.2rem;">')
    sh('<div style="padding:0 1.2rem 0.3rem;font-size:0.65rem;font-weight:700;color:#475569;letter-spacing:0.1em;text-transform:uppercase;">Clinical Workflow</div>')

    # Nav items with completion tracking
    _profile    = st.session_state.get("patient_profile")
    _risk       = st.session_state.get("risk_result")
    _med        = st.session_state.get("med_result")
    _nutr       = st.session_state.get("nutrition_result")
    _econ       = st.session_state.get("econ_result")
    _adhr       = st.session_state.get("adherence_result")

    nav_items = [
        ("Home",       "\U0001f3e0",  "Home",                    True),
        ("Risk",       "❤️",           "Kidney Risk Assessment",  bool(_risk)),
        ("Evidence",   "\U0001f50d",  "Clinical Evidence",       False),
        ("Medication", "\U0001f48a",  "Medication Intelligence",  bool(_med)),
        ("Nutrition",  "\U0001f966",  "Nutrition Intelligence",   bool(_nutr)),
        ("Economics",  "\U0001f4ca",  "Pharmacoeconomics",        bool(_econ)),
        ("Adherence",  "\U0001f3af",  "Adherence Intelligence",   bool(_adhr)),
        ("Report",     "\U0001f4c4",  "Report Generator",         False),
    ]

    for key, icon, label, done in nav_items:
        badge = " ✓" if done else ""
        if st.button(f"{icon}  {label}{badge}", key=f"nav_{key}", use_container_width=True):
            go(key)

    # ── Patient Journey Progress ───────────────────────────────────────────
    journey_steps = [
        ("Patient Profile",         bool(_profile)),
        ("Kidney Risk Assessment",  bool(_risk)),
        ("Medication Review",       bool(_med)),
        ("Nutrition Analysis",      bool(_nutr)),
        ("Economic Assessment",     bool(_econ)),
        ("Adherence Scoring",       bool(_adhr)),
    ]
    completed = sum(1 for _, d in journey_steps if d)
    pct = int(completed / len(journey_steps) * 100)
    steps_html = ''.join(
        f'<div style="display:flex;align-items:center;gap:7px;padding:3px 0;">'
        f'<div style="width:16px;height:16px;border-radius:50%;background:{"#10B981" if done else "#1E293B"};border:2px solid {"#10B981" if done else "#334155"};display:flex;align-items:center;justify-content:center;flex-shrink:0;">'
        f'<span style="font-size:0.55rem;color:white;font-weight:900;">{"✓" if done else str(i+1)}</span></div>'
        f'<span style="font-size:0.73rem;color:{"#E2E8F0" if done else "#64748B"};font-weight:{"600" if done else "400"};">{name}</span>'
        f'</div>'
        for i, (name, done) in enumerate(journey_steps)
    )
    sh(f'<div style="margin:0.8rem 0.8rem 0;border-radius:10px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);padding:0.9rem 1rem;"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.6rem;"><span style="font-size:0.65rem;font-weight:700;color:#475569;letter-spacing:0.1em;text-transform:uppercase;">Patient Journey</span><span style="font-size:0.72rem;font-weight:800;color:#14B8A6;">{pct}%</span></div><div style="background:#1E293B;border-radius:99px;height:4px;margin-bottom:0.7rem;"><div style="background:linear-gradient(90deg,#14B8A6,#6366F1);width:{pct}%;height:4px;border-radius:99px;transition:width 0.4s;"></div></div>{steps_html}</div>')

    # ── Patient Context Panel ──────────────────────────────────────────────
    profile = st.session_state.get("patient_profile")
    ctx     = st.session_state.get("patient_context")
    if ctx or profile:
        stage    = ctx.get("ckd_stage", "—")    if ctx else "—"
        risk_lv  = ctx.get("risk_category", "—") if ctx else "—"
        egfr_v   = ctx.get("egfr", "—")          if ctx else "—"
        ts       = ctx.get("last_assessed", "—")  if ctx else "—"
        adhr_sc  = ctx.get("adherence_score", None) if ctx else None
        adhr_lv  = ctx.get("adherence_level", "")   if ctx else ""
        RISK_DOT = {"Low":"#10B981","Moderate":"#F59E0B","High":"#EF4444","Critical":"#7C3AED"}
        ADHR_DOT = {"Excellent":"#10B981","Good":"#22C55E","Moderate":"#F59E0B","Poor":"#EF4444"}
        dot_c  = RISK_DOT.get(str(risk_lv), "#64748B")
        adhr_c = ADHR_DOT.get(str(adhr_lv), "#64748B")
        med_result = st.session_state.get("med_result")
        n_meds = len(getattr(med_result, "flags", [])) if med_result else 0
        # Build patient name row
        p_name = profile.get("name", "") if profile else ""
        p_age  = profile.get("age", "")  if profile else ""
        p_sex  = profile.get("gender", "")[:1] if profile else ""
        name_row = f'<div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:4px;margin-bottom:4px;border-bottom:1px solid rgba(255,255,255,0.06);"><span style="font-size:0.77rem;font-weight:700;color:#E2E8F0;">{p_name or "Anonymous Patient"}</span><span style="font-size:0.7rem;color:#64748B;">{p_age}{"y" if p_age else ""} {p_sex}</span></div>' if (p_name or p_age) else ""
        adhr_row = f'<div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-size:0.75rem;color:#94A3B8;">Adherence</span><span style="font-size:0.78rem;font-weight:700;color:{adhr_c};">&#x25cf; {adhr_lv} ({adhr_sc:.0f})</span></div>' if adhr_sc is not None else ""
        sh(f'<div style="margin:0.8rem 0.8rem 0;border-radius:10px;background:rgba(20,184,166,0.07);border:1px solid rgba(20,184,166,0.2);padding:0.9rem 1rem;"><div style="font-size:0.65rem;font-weight:700;color:#14B8A6;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.6rem;">&#x1f9d1;&#x200d;&#x2695;&#xfe0f; Patient Context</div><div style="display:flex;flex-direction:column;gap:5px;">{name_row}<div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-size:0.75rem;color:#94A3B8;">CKD Stage</span><span style="font-size:0.78rem;font-weight:700;color:#E2E8F0;">Stage {stage}</span></div><div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-size:0.75rem;color:#94A3B8;">Risk Level</span><span style="font-size:0.78rem;font-weight:700;color:{dot_c};">&#x25cf; {risk_lv}</span></div><div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-size:0.75rem;color:#94A3B8;">eGFR</span><span style="font-size:0.78rem;font-weight:700;color:#E2E8F0;">{egfr_v} mL/min</span></div><div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-size:0.75rem;color:#94A3B8;">Med Alerts</span><span style="font-size:0.78rem;font-weight:700;color:#E2E8F0;">{n_meds} flag{"s" if n_meds != 1 else ""}</span></div>{adhr_row}<div style="border-top:1px solid rgba(255,255,255,0.06);padding-top:4px;margin-top:2px;font-size:0.67rem;color:#475569;">Assessed: {ts}</div></div></div>')

    # Future modules lock block
    sh("""
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
    """)

    # Bottom user card
    sh("""
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
    """)

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
elif page == "Adherence":
    from pages.adherence_intelligence import render; render()
elif page == "Report":
    from pages.report_generator import render; render()
