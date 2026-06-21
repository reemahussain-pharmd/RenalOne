"""Patient Adherence Intelligence — Sprint 5 — RenalCare AI."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import math
import streamlit as st
from components.styles import sh

# ── Weights & thresholds ─────────────────────────────────────────────────────
DOMAIN_WEIGHTS = {
    "medication":    0.30,
    "dietary":       0.25,
    "fluid":         0.20,
    "appointments":  0.15,
    "lifestyle":     0.10,
}

DOMAIN_META = {
    "medication":   {"label": "Medication Adherence",  "icon": "💊", "color": "#6366F1"},
    "dietary":      {"label": "Dietary Adherence",     "icon": "🥦", "color": "#10B981"},
    "fluid":        {"label": "Fluid Management",      "icon": "💧", "color": "#3B82F6"},
    "appointments": {"label": "Appointment Adherence", "icon": "📅", "color": "#F59E0B"},
    "lifestyle":    {"label": "Lifestyle Modification","icon": "🏃", "color": "#EC4899"},
}

RISK_LEVELS = [
    (85, "Excellent", "#10B981", "#D1FAE5"),
    (70, "Good",      "#22C55E", "#DCFCE7"),
    (50, "Moderate",  "#F59E0B", "#FEF3C7"),
    (0,  "Poor",      "#EF4444", "#FEE2E2"),
]

AI_RECS = {
    "medication": {
        "Excellent": "Outstanding medication adherence. Continue current regimen and reinforce the importance of never self-discontinuing.",
        "Good":      "Good adherence overall. Identify any specific drugs frequently missed and discuss with pharmacist for blister pack or simplification strategies.",
        "Moderate":  "Moderate medication adherence is a significant clinical concern in CKD. Consider pill organiser, mobile reminders (apps: Medisafe, MyTherapy), and pharmacist-led CMR.",
        "Poor":      "Critical adherence gap. Urgent pharmacist-led Comprehensive Medication Review (CMR) recommended. Explore causes: side effects, polypharmacy burden, cost, health literacy.",
    },
    "dietary":    {
        "Excellent": "Excellent renal diet compliance — critical for slowing CKD progression and preventing hyperkalaemia/hyperphosphataemia.",
        "Good":      "Good dietary adherence. Reinforce potassium and phosphate limits. Referral to renal dietitian for personalised meal planning recommended.",
        "Moderate":  "Moderate dietary compliance increases risk of electrolyte crises and hospitalisation. Renal dietitian referral is strongly recommended.",
        "Poor":      "Poor dietary adherence is a high-risk finding. Immediate renal dietitian consultation and family education session needed.",
    },
    "fluid":      {
        "Excellent": "Excellent fluid management — significantly reduces interdialytic weight gain, hypertension, and cardiac complications.",
        "Good":      "Good fluid control. Continue monitoring interdialytic weight gain. Target <2.5kg between sessions.",
        "Moderate":  "Fluid non-compliance increases cardiovascular risk and reduces dialysis efficacy. Fluid chart and daily weight monitoring recommended.",
        "Poor":      "Severe fluid non-adherence. Risk of acute pulmonary oedema and cardiac decompensation. Urgent fluid restriction counselling and sodium reduction in diet.",
    },
    "appointments": {
        "Excellent": "Excellent appointment compliance — ensures consistent dialysis adequacy (Kt/V) and early complication detection.",
        "Good":      "Good attendance. Identify any logistical barriers (transport, work) to prevent missed sessions.",
        "Moderate":  "Missed dialysis sessions reduce Kt/V and increase toxin burden. Social worker assessment for transport/scheduling barriers recommended.",
        "Poor":      "Critical attendance concern. Each missed HD session increases 30-day mortality risk. Immediate social work, transport, and schedule review needed.",
    },
    "lifestyle":  {
        "Excellent": "Excellent lifestyle modification. Continue regular low-impact exercise and stress management practices.",
        "Good":      "Good lifestyle habits. Consider structured renal rehabilitation programme if not already enrolled.",
        "Moderate":  "Lifestyle optimisation is an underutilised intervention in CKD. Consider formal renal rehabilitation referral and psychological support.",
        "Poor":      "Significant lifestyle risk factors present. Address smoking cessation (priority), increase physical activity with physiotherapy guidance, and consider psychological counselling.",
    },
}

# ── Scoring logic ─────────────────────────────────────────────────────────────

def _score_medication(missed_pw, stops_meds, side_effects_skip):
    base = [60, 45, 25, 0][min(missed_pw, 3)]
    base += [20, 10, 0][min(stops_meds, 2)]
    base += [20, 10, 0][min(side_effects_skip, 2)]
    return min(100, base)

def _score_dietary(compliance_level, nutrition_in_session):
    base = [10, 35, 60, 80, 100][compliance_level]
    if nutrition_in_session:
        log = nutrition_in_session.get("log", [])
        if log and len(log) >= 3:
            # Compute average excess over limits
            totals = nutrition_in_session.get("totals", {})
            k_total  = sum(e.get("nutrients", {}).get("potassium", 0) for e in log)
            na_total = sum(e.get("nutrients", {}).get("sodium", 0) for e in log)
            po_total = sum(e.get("nutrients", {}).get("phosphate", 0) for e in log)
            days = max(len(log), 1)
            limits = {"k": 2000, "na": 1500, "po": 800}
            ratios = [k_total/days/limits["k"], na_total/days/limits["na"], po_total/days/limits["po"]]
            avg_ratio = sum(ratios) / 3
            if avg_ratio <= 0.8:   auto = 100
            elif avg_ratio <= 1.0: auto = 85
            elif avg_ratio <= 1.2: auto = 60
            elif avg_ratio <= 1.5: auto = 35
            else:                  auto = 10
            # blend questionnaire and auto
            base = round(0.4 * base + 0.6 * auto)
    return min(100, base)

def _score_fluid(daily_ml, limit_ml):
    ratio = daily_ml / max(limit_ml, 1)
    if ratio <= 1.00: return 100
    if ratio <= 1.15: return 80
    if ratio <= 1.35: return 55
    if ratio <= 1.75: return 30
    return 5

def _score_appointments(attended, total, clinic_missed):
    appt = min(1.0, attended / max(total, 1)) * 70
    appt += [30, 15, 0][min(clinic_missed, 2)]
    return min(100, round(appt))

def _score_lifestyle(smoking_idx, exercise_idx, alcohol_idx, stress_idx):
    s  = [0, 10, 20, 30][min(smoking_idx, 3)]   # Current=0, Reduced=10, Former=20, Never=30
    e  = [0, 10, 20, 30][min(exercise_idx, 3)]  # Never=0, Rarely=10, Sometimes=20, Regular=30
    a  = [0, 5, 15, 20][min(alcohol_idx, 3)]    # Daily=0, Regular=5, Occasional=15, None=20
    st_ = [0, 10, 20][min(stress_idx, 2)]        # No=0, Sometimes=10, Yes=20
    return min(100, s + e + a + st_)

def _risk_for_score(score):
    for threshold, label, color, bg in RISK_LEVELS:
        if score >= threshold:
            return label, color, bg
    return "Poor", "#EF4444", "#FEE2E2"


# ── Render ────────────────────────────────────────────────────────────────────

def render():
    sh("""
    <div class="page-header">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;">
            <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.5rem;">
                    <span style="font-size:1.5rem;">&#x1f3af;</span>
                    <span style="background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.9);font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:20px;letter-spacing:0.06em;">5-DOMAIN SCORING</span>
                    <span style="background:rgba(99,102,241,0.3);color:#C7D2FE;font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:20px;">Sprint 5 &#x2014; New Module</span>
                </div>
                <h1 style="color:white !important;font-size:1.7rem !important;font-weight:800 !important;margin:0 0 0.3rem 0 !important;">Patient Adherence Intelligence</h1>
                <p style="color:rgba(255,255,255,0.72) !important;font-size:0.88rem !important;margin:0 !important;">
                    Medication &bull; Dietary &bull; Fluid Management &bull; Appointments &bull; Lifestyle Modification
                </p>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.7rem;color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:0.07em;">Evidence Base</div>
                <div style="font-size:0.82rem;color:rgba(255,255,255,0.85);font-weight:600;">KDIGO 2024</div>
                <div style="font-size:0.82rem;color:rgba(255,255,255,0.85);font-weight:600;">Morisky MMAS-8</div>
            </div>
        </div>
    </div>
    """)

    # Check if nutrition data is available
    nutrition_in_session = st.session_state.get("nutrition_result")
    patient_profile = st.session_state.get("patient_profile")

    if patient_profile:
        sh(f'<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;padding:0.6rem 1rem;margin-bottom:0.6rem;font-size:0.82rem;display:flex;align-items:center;gap:8px;"><span style="color:#1D4ED8;font-weight:700;">&#x1f464; {patient_profile.get("name","Patient")}</span><span style="color:#94A3B8;">|</span><span style="color:#374151;">{patient_profile.get("age","—")} yrs &bull; {patient_profile.get("gender","—")} &bull; {patient_profile.get("dialysis_type","CKD")}</span></div>')

    if nutrition_in_session:
        sh('<div style="background:#D1FAE5;border:1px solid #6EE7B7;border-radius:8px;padding:0.5rem 1rem;margin-bottom:0.6rem;font-size:0.78rem;color:#065F46;"><strong>&#x2713; Nutrition log detected</strong> — dietary domain will be partially auto-scored from your logged food entries.</div>')

    left_col, right_col = st.columns([1.1, 1.5])

    with left_col:
        with st.form("adherence_form"):
            # ── Domain 1: Medication ────────────────────────────────────────
            sh('<div class="section-title-accent"><span>&#x1f48a;</span> Domain 1 — Medication Adherence <span style="font-size:0.68rem;color:#94A3B8;font-weight:500;">(30% weight)</span></div>')
            missed_pw = st.selectbox("Doses missed per week (on average)",
                ["0 — Never miss a dose", "1 — Miss ~1 dose/week", "2 — Miss ~2 doses/week", "3+ — Miss 3 or more/week"])
            missed_idx = ["0 — Never miss a dose","1 — Miss ~1 dose/week","2 — Miss ~2 doses/week","3+ — Miss 3 or more/week"].index(missed_pw)

            stops_meds = st.selectbox("Stop medications when you feel better?",
                ["Never", "Sometimes", "Often / Always"])
            stops_idx = ["Never","Sometimes","Often / Always"].index(stops_meds)

            side_effects = st.selectbox("Skip doses due to side effects?",
                ["Never", "Sometimes", "Often / Always"])
            side_idx = ["Never","Sometimes","Often / Always"].index(side_effects)

            # ── Domain 2: Dietary ───────────────────────────────────────────
            sh('<div class="section-title-accent" style="margin-top:0.8rem;"><span>&#x1f966;</span> Domain 2 — Dietary Adherence <span style="font-size:0.68rem;color:#94A3B8;font-weight:500;">(25% weight)</span></div>')
            diet_compliance = st.selectbox("How closely do you follow your renal diet?",
                ["Never follow it", "Rarely (1-2 days/week)", "Sometimes (3-4 days/week)", "Usually (5-6 days/week)", "Always (every day)"])
            diet_idx = ["Never follow it","Rarely (1-2 days/week)","Sometimes (3-4 days/week)","Usually (5-6 days/week)","Always (every day)"].index(diet_compliance)

            # ── Domain 3: Fluid ─────────────────────────────────────────────
            sh('<div class="section-title-accent" style="margin-top:0.8rem;"><span>&#x1f4a7;</span> Domain 3 — Fluid Management <span style="font-size:0.68rem;color:#94A3B8;font-weight:500;">(20% weight)</span></div>')
            fl_c1, fl_c2 = st.columns(2)
            with fl_c1:
                daily_fluid = st.number_input("Avg daily fluid intake (mL)", 100, 5000, 1000, step=100)
            with fl_c2:
                fluid_limit = st.number_input("Prescribed fluid limit (mL)", 250, 3000, 750, step=50,
                                              help="Typical HD: 500–750 mL/day between sessions")

            # ── Domain 4: Appointments ──────────────────────────────────────
            sh('<div class="section-title-accent" style="margin-top:0.8rem;"><span>&#x1f4c5;</span> Domain 4 — Appointment Adherence <span style="font-size:0.68rem;color:#94A3B8;font-weight:500;">(15% weight)</span></div>')
            ap_c1, ap_c2 = st.columns(2)
            with ap_c1:
                sessions_attended = st.number_input("Dialysis sessions attended (last 12 scheduled)", 0, 12, 11)
            with ap_c2:
                clinic_missed = st.selectbox("Nephrology clinic appointments missed (3 months)",
                    ["0 — None missed", "1 — Missed one", "2+ — Missed two or more"])
            clinic_idx = ["0 — None missed","1 — Missed one","2+ — Missed two or more"].index(clinic_missed)

            # ── Domain 5: Lifestyle ─────────────────────────────────────────
            sh('<div class="section-title-accent" style="margin-top:0.8rem;"><span>&#x1f3c3;</span> Domain 5 — Lifestyle Modification <span style="font-size:0.68rem;color:#94A3B8;font-weight:500;">(10% weight)</span></div>')
            ls_c1, ls_c2 = st.columns(2)
            with ls_c1:
                smoking = st.selectbox("Smoking status",
                    ["Never smoked", "Former smoker (quit)", "Reduced / cutting down", "Current smoker"])
                smoking_idx = ["Never smoked","Former smoker (quit)","Reduced / cutting down","Current smoker"].index(smoking)
                smoking_idx = 3 - smoking_idx  # Reverse: Never=3, Former=2, Reduced=1, Current=0

                exercise = st.selectbox("Exercise / physical activity",
                    ["Regular (≥3×/week)", "Sometimes (1-2×/week)", "Rarely (<1×/week)", "Never"])
                exercise_idx = ["Regular (≥3×/week)","Sometimes (1-2×/week)","Rarely (<1×/week)","Never"].index(exercise)
                exercise_idx = 3 - exercise_idx  # Reverse: Regular=3 → score 30
            with ls_c2:
                alcohol = st.selectbox("Alcohol consumption",
                    ["None", "Occasional (1-2/week)", "Regular (>3/week)", "Daily"])
                alcohol_idx = ["None","Occasional (1-2/week)","Regular (>3/week)","Daily"].index(alcohol)
                alcohol_idx = 3 - alcohol_idx  # Reverse: None=3 → score 20

                stress_mgmt = st.selectbox("Actively manage stress / mental health?",
                    ["Yes, actively (yoga/therapy/mindfulness)", "Sometimes", "No"])
                stress_idx = ["Yes, actively (yoga/therapy/mindfulness)","Sometimes","No"].index(stress_mgmt)
                stress_idx = 2 - stress_idx  # Reverse: Yes=2 → score 20

            submitted = st.form_submit_button("&#x1f3af;  Calculate Adherence Score",
                                              use_container_width=True, type="primary")

    with right_col:
        if submitted:
            # ── Compute domain scores ───────────────────────────────────────
            domains = {
                "medication":    _score_medication(missed_idx, stops_idx, side_idx),
                "dietary":       _score_dietary(diet_idx, nutrition_in_session),
                "fluid":         _score_fluid(daily_fluid, fluid_limit),
                "appointments":  _score_appointments(sessions_attended, 12, clinic_idx),
                "lifestyle":     _score_lifestyle(smoking_idx, exercise_idx, alcohol_idx, stress_idx),
            }
            overall = sum(domains[k] * DOMAIN_WEIGHTS[k] for k in DOMAIN_WEIGHTS)
            overall = round(overall, 1)
            risk_label, risk_color, risk_bg = _risk_for_score(overall)

            # Persist to session state for sidebar + PDF
            st.session_state.adherence_result = {
                "overall": overall,
                "risk_level": risk_label,
                "color": risk_color,
                "domains": domains,
            }
            st.session_state.patient_context = {
                **st.session_state.get("patient_context", {}),
                "adherence_score": overall,
                "adherence_level": risk_label,
            }

        if st.session_state.get("adherence_result"):
            r = st.session_state.adherence_result
            _render_results(r)
        elif not submitted:
            _render_placeholder()


def _render_results(r):
    overall    = r["overall"]
    risk_label = r["risk_level"]
    risk_color = r["color"]
    _, _, risk_bg = _risk_for_score(overall)
    domains    = r["domains"]

    # ── Overall score ring + KPIs ─────────────────────────────────────────
    sh(f'<div style="background:{risk_bg};border:2px solid {risk_color}40;border-radius:14px;padding:1.1rem 1.4rem;margin-bottom:0.8rem;display:flex;align-items:center;gap:1.5rem;"><div style="width:80px;height:80px;border-radius:50%;background:conic-gradient({risk_color} {overall*3.6:.0f}deg,#E2E8F0 0deg);display:flex;align-items:center;justify-content:center;flex-shrink:0;position:relative;"><div style="width:60px;height:60px;border-radius:50%;background:{risk_bg};display:flex;align-items:center;justify-content:center;"><span style="font-size:1rem;font-weight:900;color:{risk_color};">{overall:.0f}</span></div></div><div><div style="font-size:0.7rem;font-weight:700;color:{risk_color};text-transform:uppercase;letter-spacing:0.09em;">Overall Adherence Score</div><div style="font-size:1.6rem;font-weight:900;color:{risk_color};line-height:1.1;">{overall:.1f}<span style="font-size:0.9rem;font-weight:500;color:#64748B;">/100</span></div><div style="font-size:0.9rem;font-weight:700;color:{risk_color};margin-top:2px;">{risk_label} Adherence</div><div style="font-size:0.76rem;color:#64748B;margin-top:2px;">Weighted across 5 clinical domains</div></div></div>')

    # ── Radar chart ───────────────────────────────────────────────────────
    try:
        import plotly.graph_objects as go

        domain_keys   = list(DOMAIN_WEIGHTS.keys())
        domain_labels = [DOMAIN_META[k]["label"].split(" Adhe")[0].split(" Mgmt")[0].split(" Mod")[0] for k in domain_keys]
        domain_vals   = [domains[k] for k in domain_keys]
        domain_vals_closed = domain_vals + [domain_vals[0]]
        domain_labels_closed = domain_labels + [domain_labels[0]]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=domain_vals_closed,
            theta=domain_labels_closed,
            fill="toself",
            fillcolor=f"rgba(99,102,241,0.18)",
            line=dict(color="#6366F1", width=2.5),
            name="Patient Score",
            hovertemplate="%{theta}: %{r:.0f}/100<extra></extra>",
        ))
        fig.add_trace(go.Scatterpolar(
            r=[100] * (len(domain_labels) + 1),
            theta=domain_labels_closed,
            fill="toself",
            fillcolor="rgba(226,232,240,0.12)",
            line=dict(color="#CBD5E1", width=1, dash="dot"),
            name="Max (100)",
            hovertemplate="%{theta}: Max 100<extra></extra>",
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=8), gridcolor="#F1F5F9"),
                angularaxis=dict(tickfont=dict(size=9, color="#374151")),
                bgcolor="rgba(248,250,252,0.8)",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center", font=dict(size=9)),
            margin=dict(l=30, r=30, t=20, b=40),
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    except Exception:
        pass

    # ── Domain breakdown ──────────────────────────────────────────────────
    sh('<div class="section-title"><span>&#x1f4ca;</span> Domain Breakdown</div>')
    for key in DOMAIN_WEIGHTS:
        meta   = DOMAIN_META[key]
        score  = domains[key]
        d_label, d_color, d_bg = _risk_for_score(score)
        wt_pct = int(DOMAIN_WEIGHTS[key] * 100)
        sh(f'<div style="background:white;border:1px solid #E2E8F0;border-radius:10px;padding:0.75rem 0.9rem;margin-bottom:0.45rem;"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.4rem;"><div style="display:flex;align-items:center;gap:7px;"><span style="font-size:0.95rem;">{meta["icon"]}</span><span style="font-size:0.83rem;font-weight:700;color:#0F172A;">{meta["label"]}</span><span style="background:#F1F5F9;color:#64748B;font-size:0.62rem;font-weight:700;padding:1px 6px;border-radius:4px;">{wt_pct}% weight</span></div><div style="display:flex;align-items:center;gap:6px;"><span style="font-size:0.88rem;font-weight:800;color:{d_color};">{score:.0f}/100</span><span style="background:{d_bg};color:{d_color};font-size:0.65rem;font-weight:700;padding:2px 7px;border-radius:999px;">{d_label}</span></div></div><div style="background:#F1F5F9;border-radius:999px;height:5px;margin-bottom:0.4rem;"><div style="background:{meta["color"]};width:{score}%;height:5px;border-radius:999px;transition:width 0.4s;"></div></div><div style="font-size:0.76rem;color:#475569;line-height:1.5;">{AI_RECS[key][d_label]}</div></div>')

    # ── Evidence-based interventions ──────────────────────────────────────
    _render_evidence_interventions(domains)


def _render_evidence_interventions(domains):
    sh('<div style="margin-top:0.8rem;"></div>')
    sh('<div class="section-title"><span>&#x1f4da;</span> Evidence-Based Intervention Priorities</div>')

    # Sort domains by score (lowest first = highest priority)
    sorted_domains = sorted(domains.items(), key=lambda x: x[1])
    priority_domains = [k for k, v in sorted_domains if v < 70][:3]

    if not priority_domains:
        sh('<div style="background:#D1FAE5;border:1px solid #6EE7B7;border-radius:10px;padding:0.8rem 1rem;font-size:0.83rem;color:#065F46;"><strong>&#x2705; Excellent overall adherence profile.</strong> No urgent intervention priorities identified. Continue current strategies and schedule routine 3-monthly adherence reassessment.</div>')
        return

    interventions = {
        "medication":   ("Comprehensive Medication Review (CMR)", "Pharmacist", "NICE NG5 / KDIGO 2024", "#6366F1"),
        "dietary":      ("Renal Dietitian Referral + Dietary Education", "Dietitian", "KDIGO 2024, K/DOQI", "#10B981"),
        "fluid":        ("Fluid Restriction Counselling + Daily Weight Monitoring", "Nurse/Dietitian", "KDIGO 2024", "#3B82F6"),
        "appointments": ("Social Work Assessment — Transport & Schedule Barriers", "Social Worker", "KHA-CARI 2023", "#F59E0B"),
        "lifestyle":    ("Renal Rehabilitation Referral + Behavioural Support", "Physiotherapist/Psychologist", "KDIGO 2024", "#EC4899"),
    }

    for i, key in enumerate(priority_domains):
        meta    = DOMAIN_META[key]
        score   = domains[key]
        label, ref, clinician, btn_c = interventions[key][0], interventions[key][2], interventions[key][1], interventions[key][3]
        priority_badge = ["URGENT", "HIGH PRIORITY", "RECOMMENDED"][i]
        priority_bg    = ["#FEE2E2", "#FEF3C7", "#EFF6FF"][i]
        priority_c     = ["#991B1B", "#92400E", "#1D4ED8"][i]
        sh(f'<div style="background:{priority_bg};border:1px solid {priority_c}20;border-radius:10px;padding:0.8rem 1rem;margin-bottom:0.5rem;"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.4rem;"><div style="display:flex;align-items:center;gap:7px;"><span style="background:{priority_c};color:white;font-size:0.62rem;font-weight:800;padding:2px 8px;border-radius:4px;letter-spacing:0.06em;">{priority_badge}</span><span style="font-size:0.83rem;font-weight:700;color:#0F172A;">{meta["icon"]} {meta["label"]}</span></div><span style="font-size:0.78rem;font-weight:700;color:{priority_c};">{score:.0f}/100</span></div><div style="font-size:0.83rem;font-weight:700;color:#1E293B;margin-bottom:2px;">{label}</div><div style="display:flex;gap:8px;font-size:0.73rem;color:#64748B;"><span>&#x1f468;&#x200d;&#x2695;&#xfe0f; {clinician}</span><span>&bull;</span><span>&#x1f4cb; {ref}</span></div></div>')


def _render_placeholder():
    sh("""
    <div style="background:white;border:2px dashed #E2E8F0;border-radius:16px;padding:3rem;text-align:center;">
        <div style="font-size:3rem;margin-bottom:1rem;">&#x1f3af;</div>
        <div style="font-size:1rem;font-weight:700;color:#0F172A;margin-bottom:0.5rem;">Patient Adherence Intelligence</div>
        <div style="font-size:0.84rem;color:#64748B;max-width:420px;margin:0 auto;line-height:1.6;">
            Complete the 5-domain adherence questionnaire to generate a comprehensive
            patient adherence profile with evidence-based intervention recommendations.
        </div>
        <div style="margin-top:1.5rem;display:flex;gap:8px;justify-content:center;flex-wrap:wrap;">
            <span style="background:#EEF2FF;color:#3730A3;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">&#x1f48a; Medication</span>
            <span style="background:#D1FAE5;color:#065F46;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">&#x1f966; Dietary</span>
            <span style="background:#EFF6FF;color:#1D4ED8;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">&#x1f4a7; Fluid</span>
            <span style="background:#FEF3C7;color:#92400E;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">&#x1f4c5; Appointments</span>
            <span style="background:#FCE7F3;color:#9D174D;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">&#x1f3c3; Lifestyle</span>
        </div>
    </div>
    """)
