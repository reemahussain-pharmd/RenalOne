"""Kidney Risk Assessment Page — RenalCare AI."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from models.kidney_risk import RiskInput, calculate_risk
from components.charts import risk_gauge, risk_factor_bar


RISK_CONFIG = {
    "LOW":      ("#10B981", "#D1FAE5", "#065F46"),
    "MODERATE": ("#F59E0B", "#FEF3C7", "#92400E"),
    "HIGH":     ("#EF4444", "#FEE2E2", "#991B1B"),
    "CRITICAL": ("#7C3AED", "#EDE9FE", "#4C1D95"),
}

CKD_STAGE_DESC = {
    "G1":  ("Normal or High",           ">= 90",  "#10B981"),
    "G2":  ("Mildly Decreased",         "60-89",  "#3B82F6"),
    "G3a": ("Mildly-Moderately Decr.",  "45-59",  "#F59E0B"),
    "G3b": ("Moderately-Severely Decr.","30-44",  "#F97316"),
    "G4":  ("Severely Decreased",       "15-29",  "#EF4444"),
    "G5":  ("Kidney Failure",           "< 15",   "#7C3AED"),
}

ALBUMIN_MAP = {
    "A1: Normal (<30 mg/g)":                  "None",
    "A2: Moderately Elevated (30-300 mg/g)":  "Microalbuminuria",
    "A3: Severely Elevated (>300 mg/g)":      "Macroalbuminuria",
}

IMPACT_SCORE = {"Low": 4, "Moderate": 8, "High": 15, "Critical": 25}


def render():
    st.markdown("""
    <div class="page-header">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;">
            <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.5rem;">
                    <span style="font-size:1.5rem;">❤️</span>
                    <span style="background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.9);
                                 font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:20px;
                                 letter-spacing:0.06em;">KDIGO 2024 RISK MODEL</span>
                </div>
                <h1 style="color:white !important;font-size:1.7rem !important;font-weight:800 !important;
                           margin:0 0 0.3rem 0 !important;">Kidney Risk Assessment</h1>
                <p style="color:rgba(255,255,255,0.72) !important;font-size:0.88rem !important;margin:0 !important;">
                    Multi-variable CKD risk stratification using eGFR, albuminuria, comorbidities &amp; lifestyle factors
                </p>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.7rem;color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:0.07em;">Model</div>
                <div style="font-size:0.85rem;color:rgba(255,255,255,0.85);font-weight:600;">CKD-EPI 2021</div>
                <div style="font-size:0.85rem;color:rgba(255,255,255,0.85);font-weight:600;">KDIGO Heat Map</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([1.1, 1.5])

    with left_col:
        with st.form("risk_form"):
            st.markdown('<div class="section-title-accent"><span>\U0001f464</span> Demographics</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                age = st.number_input("Age (years)", 18, 100, 58)
            with c2:
                gender = st.selectbox("Sex", ["Male", "Female"])

            c3, c4 = st.columns(2)
            with c3:
                weight = st.number_input("Weight (kg)", 30.0, 200.0, 72.0, 0.5)
            with c4:
                height = st.number_input("Height (cm)", 130, 220, 168)

            st.markdown('<div class="section-title-accent" style="margin-top:0.8rem;"><span>\U0001f9ea</span> Laboratory Values</div>', unsafe_allow_html=True)
            c5, c6 = st.columns(2)
            with c5:
                egfr = st.number_input("eGFR (mL/min/1.73m²)", 1, 150, 38)
            with c6:
                creatinine = st.number_input("Creatinine (mg/dL)", 0.4, 15.0, 2.1, 0.1)

            c7, c8 = st.columns(2)
            with c7:
                albumin_label = st.selectbox("Urine Albumin (UACR)", list(ALBUMIN_MAP.keys()))
            with c8:
                hba1c = st.number_input("HbA1c (%) — if diabetic", 4.0, 15.0, 7.8, 0.1)

            c_bp1, c_bp2 = st.columns(2)
            with c_bp1:
                sbp = st.number_input("Systolic BP (mmHg)", 90, 220, 148)
            with c_bp2:
                dbp = st.number_input("Diastolic BP (mmHg)", 50, 140, 92)

            st.markdown('<div class="section-title-accent" style="margin-top:0.8rem;"><span>\U0001f3e5</span> Comorbidities</div>', unsafe_allow_html=True)
            ca, cb = st.columns(2)
            with ca:
                diabetes     = st.checkbox("Diabetes Mellitus", value=True)
                hypertension = st.checkbox("Hypertension", value=True)
                smoking      = st.checkbox("Current Smoker")
            with cb:
                alcohol      = st.checkbox("Regular Alcohol Use")
                family_hx    = st.checkbox("Family History of CKD")

            submitted = st.form_submit_button(
                "\U0001f50d  Calculate Risk Score",
                use_container_width=True,
                type="primary",
            )

    with right_col:
        if submitted:
            bmi = weight / ((height / 100) ** 2)
            inp = RiskInput(
                age=float(age),
                gender=gender,
                weight_kg=float(weight),
                height_cm=float(height),
                bmi=round(bmi, 1),
                diabetes=diabetes,
                hypertension=hypertension,
                smoking=smoking,
                alcohol=alcohol,
                family_history=family_hx,
                serum_creatinine=float(creatinine),
                egfr=float(egfr),
                albuminuria=ALBUMIN_MAP[albumin_label],
                hba1c=float(hba1c) if diabetes else None,
                systolic_bp=float(sbp),
                diastolic_bp=float(dbp),
            )
            result = calculate_risk(inp)
            st.session_state.risk_result = result
            _render_results(result, egfr, bmi)
        elif st.session_state.get("risk_result"):
            st.markdown("""
            <div class="alert alert-info" style="margin-bottom:0.8rem;">
                Showing previous assessment — adjust inputs and re-run to update.
            </div>
            """, unsafe_allow_html=True)
            _render_placeholder()
        else:
            _render_placeholder()


def _render_results(result, egfr, bmi):
    risk = result.risk_category.upper()
    color, bg, text_color = RISK_CONFIG.get(risk, RISK_CONFIG["MODERATE"])

    # ── Risk banner ────────────────────────────────────────────────────────
    stage_num = result.ckd_stage_num
    st.markdown(f"""
    <div style="background:{bg};border:2px solid {color};border-radius:14px;
                padding:1.2rem 1.5rem;margin-bottom:1.2rem;">
        <div style="display:flex;align-items:center;justify-content:space-between;">
            <div>
                <div style="font-size:0.72rem;font-weight:700;color:{color};
                            letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.3rem;">
                    CKD Risk Level
                </div>
                <div style="font-size:1.6rem;font-weight:900;color:{color};">{risk} RISK</div>
                <div style="font-size:0.83rem;color:#334155;margin-top:0.3rem;">
                    CKD Stage <strong>{stage_num}</strong> &bull;
                    eGFR <strong>{egfr} mL/min</strong> &bull;
                    BMI <strong>{bmi:.1f}</strong>
                </div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:2.5rem;font-weight:900;color:{color};">{result.risk_score:.0f}</div>
                <div style="font-size:0.7rem;font-weight:700;color:{color};letter-spacing:0.06em;text-transform:uppercase;">/ 100</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Gauge chart ────────────────────────────────────────────────────────
    try:
        fig = risk_gauge(result.risk_score, result.risk_category)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    except Exception:
        pass

    # ── CKD Stage badge ────────────────────────────────────────────────────
    if stage_num in CKD_STAGE_DESC:
        s_label, s_range, s_color = CKD_STAGE_DESC[stage_num]
        st.markdown(f"""
        <div style="background:white;border:1px solid #E2E8F0;border-radius:10px;
                    padding:0.9rem 1.1rem;margin-bottom:0.8rem;">
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <div>
                    <div style="font-size:0.72rem;font-weight:700;color:#64748B;
                                letter-spacing:0.06em;text-transform:uppercase;">CKD Classification</div>
                    <div style="font-size:1.1rem;font-weight:800;color:#0F172A;">
                        Stage {stage_num} — {s_label}
                    </div>
                </div>
                <div style="background:{s_color}15;border:1px solid {s_color}40;border-radius:8px;
                            padding:5px 14px;font-size:0.82rem;font-weight:700;color:{s_color};">
                    eGFR {s_range}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Contributing factors chart ─────────────────────────────────────────
    if result.contributing_factors:
        factor_scores = {}
        for f in result.contributing_factors:
            name  = f.get("factor", "Unknown")
            impact = f.get("impact", "Moderate")
            factor_scores[name] = IMPACT_SCORE.get(impact, 8)
        try:
            fig2 = risk_factor_bar(factor_scores)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        except Exception:
            pass

    # ── Recommendations ────────────────────────────────────────────────────
    if result.recommendations:
        st.markdown('<div class="section-title"><span>\U0001f4cb</span> Clinical Recommendations</div>', unsafe_allow_html=True)
        for i, rec in enumerate(result.recommendations, 1):
            p_color = "#EF4444" if i <= 2 else ("#F59E0B" if i <= 4 else "#64748B")
            p_label = "HIGH" if i <= 2 else ("MODERATE" if i <= 4 else "ROUTINE")
            st.markdown(f"""
            <div style="background:white;border:1px solid #E2E8F0;border-radius:8px;
                        padding:0.75rem 1rem;margin-bottom:0.4rem;
                        border-left:3px solid {p_color};display:flex;gap:10px;align-items:flex-start;">
                <div style="background:{p_color}20;color:{p_color};font-size:0.65rem;font-weight:800;
                            padding:2px 7px;border-radius:4px;letter-spacing:0.05em;
                            flex-shrink:0;margin-top:1px;">{p_label}</div>
                <div style="font-size:0.84rem;color:#334155;line-height:1.5;">{rec}</div>
            </div>
            """, unsafe_allow_html=True)


def _render_placeholder():
    st.markdown("""
    <div style="background:white;border:2px dashed #E2E8F0;border-radius:16px;
                padding:3rem;text-align:center;margin-top:0.5rem;">
        <div style="font-size:3rem;margin-bottom:1rem;">❤️</div>
        <div style="font-size:1rem;font-weight:700;color:#0F172A;margin-bottom:0.5rem;">
            Kidney Risk Assessment
        </div>
        <div style="font-size:0.84rem;color:#64748B;max-width:380px;margin:0 auto;line-height:1.6;">
            Enter patient demographics, laboratory values, and comorbidities to generate
            a comprehensive CKD risk stratification using the KDIGO 2024 heat map model.
        </div>
        <div style="margin-top:1.5rem;display:flex;gap:8px;justify-content:center;flex-wrap:wrap;">
            <span style="background:#FEE2E2;color:#991B1B;font-size:0.78rem;font-weight:600;
                         padding:5px 12px;border-radius:8px;">eGFR-Based Staging</span>
            <span style="background:#EFF6FF;color:#1E40AF;font-size:0.78rem;font-weight:600;
                         padding:5px 12px;border-radius:8px;">Albuminuria Category</span>
            <span style="background:#F0FDF4;color:#065F46;font-size:0.78rem;font-weight:600;
                         padding:5px 12px;border-radius:8px;">Risk Score 0-100</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
