"""Kidney Risk Assessment Page — RenalOne."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from datetime import datetime
from components.styles import sh
from models.kidney_risk import RiskInput, calculate_risk
from components.charts import risk_gauge, risk_factor_bar


RISK_CONFIG = {
    "LOW":      ("#10B981", "#D1FAE5", "#065F46"),
    "MODERATE": ("#F59E0B", "#FEF3C7", "#92400E"),
    "HIGH":     ("#EF4444", "#FEE2E2", "#991B1B"),
    "CRITICAL": ("#7C3AED", "#EDE9FE", "#4C1D95"),
}

CKD_STAGE_DESC = {
    "G1":  ("Normal or High",            ">= 90",  "#10B981"),
    "G2":  ("Mildly Decreased",          "60-89",  "#3B82F6"),
    "G3a": ("Mildly-Moderately Decr.",   "45-59",  "#F59E0B"),
    "G3b": ("Moderately-Severely Decr.", "30-44",  "#F97316"),
    "G4":  ("Severely Decreased",        "15-29",  "#EF4444"),
    "G5":  ("Kidney Failure",            "< 15",   "#7C3AED"),
}

ALBUMIN_MAP = {
    "A1: Normal (<30 mg/g)":                  "None",
    "A2: Moderately Elevated (30-300 mg/g)":  "Microalbuminuria",
    "A3: Severely Elevated (>300 mg/g)":      "Macroalbuminuria",
}

# Maps display label → albuminuria column index (0-based)
ALBUMIN_COL = {
    "A1: Normal (<30 mg/g)":                 0,
    "A2: Moderately Elevated (30-300 mg/g)": 1,
    "A3: Severely Elevated (>300 mg/g)":     2,
}

IMPACT_SCORE = {"Low": 4, "Moderate": 8, "High": 15, "Critical": 25}

# KDIGO G×A risk matrix: rows=G1..G5, cols=A1/A2/A3
# Each cell: (background_color, text_color, label)
_G = "#10B981"; _GT = "#065F46"    # green  — Low
_Y = "#F59E0B"; _YT = "#78350F"    # amber  — Moderately Increased
_O = "#EF4444"; _OT = "#7F1D1D"    # red    — High / Very High
_P = "#7C3AED"; _PT = "#2E1065"    # purple — Critically High

KDIGO_MATRIX = [
    # A1              A2              A3
    [(_G,_GT,"Low"), (_Y,_YT,"Mod↑"), (_O,_OT,"High")],      # G1
    [(_G,_GT,"Low"), (_Y,_YT,"Mod↑"), (_O,_OT,"High")],      # G2
    [(_Y,_YT,"Mod↑"),(_O,_OT,"High"), (_O,_OT,"Very High")], # G3a
    [(_O,_OT,"High"),(_O,_OT,"Very High"),(_O,_OT,"Very High")], # G3b
    [(_O,_OT,"Very High"),(_O,_OT,"Very High"),(_P,_PT,"Crit.")], # G4
    [(_P,_PT,"Crit."),(_P,_PT,"Crit."),(_P,_PT,"Crit.")],    # G5
]

GFR_ROWS = [
    ("G1", "≥ 90"),
    ("G2", "60-89"),
    ("G3a","45-59"),
    ("G3b","30-44"),
    ("G4", "15-29"),
    ("G5", "< 15"),
]


def _egfr_to_row(egfr: float) -> int:
    if egfr >= 90:  return 0
    if egfr >= 60:  return 1
    if egfr >= 45:  return 2
    if egfr >= 30:  return 3
    if egfr >= 15:  return 4
    return 5


def render():
    sh("""
    <div class="page-header">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;">
            <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.5rem;">
                    <span style="font-size:1.5rem;">&#x2764;&#xfe0f;</span>
                    <span style="background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.9);font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:20px;letter-spacing:0.06em;">KDIGO 2024 RISK MODEL</span>
                </div>
                <h1 style="color:white !important;font-size:1.7rem !important;font-weight:800 !important;margin:0 0 0.3rem 0 !important;">Kidney Risk Assessment</h1>
                <p style="color:rgba(255,255,255,0.72) !important;font-size:0.88rem !important;margin:0 !important;">Multi-variable CKD risk stratification with explainable AI scoring &amp; KDIGO G&times;A heat map</p>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.7rem;color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:0.07em;">Model</div>
                <div style="font-size:0.85rem;color:rgba(255,255,255,0.85);font-weight:600;">CKD-EPI 2021</div>
                <div style="font-size:0.85rem;color:rgba(255,255,255,0.85);font-weight:600;">KDIGO Heat Map</div>
            </div>
        </div>
    </div>
    """)

    left_col, right_col = st.columns([1.1, 1.5])

    with left_col:
        with st.form("risk_form"):
            sh('<div class="section-title-accent"><span>\U0001f464</span> Demographics</div>')
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

            sh('<div class="section-title-accent" style="margin-top:0.8rem;"><span>\U0001f9ea</span> Laboratory Values</div>')
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

            sh('<div class="section-title-accent" style="margin-top:0.8rem;"><span>\U0001f3e5</span> Comorbidities</div>')
            ca, cb = st.columns(2)
            with ca:
                diabetes     = st.checkbox("Diabetes Mellitus", value=True)
                hypertension = st.checkbox("Hypertension", value=True)
                smoking      = st.checkbox("Current Smoker")
            with cb:
                alcohol   = st.checkbox("Regular Alcohol Use")
                family_hx = st.checkbox("Family History of CKD")

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
            # Persist patient context for sidebar and other modules
            st.session_state.patient_context = {
                "ckd_stage":     result.ckd_stage_num,
                "risk_category": result.risk_category,
                "egfr":          egfr,
                "last_assessed": datetime.now().strftime("%d %b %Y %H:%M"),
            }
            _render_results(result, egfr, bmi, albumin_label)
        elif st.session_state.get("risk_result"):
            sh("""<div class="alert alert-info" style="margin-bottom:0.8rem;">Showing previous assessment — adjust inputs and re-run to update.</div>""")
            _render_placeholder()
        else:
            _render_placeholder()


def _render_results(result, egfr, bmi, albumin_label):
    risk = result.risk_category.upper()
    color, bg, text_color = RISK_CONFIG.get(risk, RISK_CONFIG["MODERATE"])

    # ── Risk banner ───────────────────────────────────────────────────────────
    stage_num = result.ckd_stage_num
    sh(f"""
    <div style="background:{bg};border:2px solid {color};border-radius:14px;padding:1.2rem 1.5rem;margin-bottom:1rem;">
        <div style="display:flex;align-items:center;justify-content:space-between;">
            <div>
                <div style="font-size:0.72rem;font-weight:700;color:{color};letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.3rem;">CKD Risk Level</div>
                <div style="font-size:1.6rem;font-weight:900;color:{color};">{risk} RISK</div>
                <div style="font-size:0.83rem;color:#334155;margin-top:0.3rem;">
                    CKD Stage <strong>{stage_num}</strong> &bull; eGFR <strong>{egfr} mL/min</strong> &bull; BMI <strong>{bmi:.1f}</strong>
                </div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:2.5rem;font-weight:900;color:{color};">{result.risk_score:.0f}</div>
                <div style="font-size:0.7rem;font-weight:700;color:{color};letter-spacing:0.06em;text-transform:uppercase;">/ 100</div>
            </div>
        </div>
    </div>
    """)

    # ── Explainable Risk Breakdown ────────────────────────────────────────────
    if result.contributing_factors:
        _render_explainability(result.contributing_factors, result.risk_score)

    # ── Gauge chart ───────────────────────────────────────────────────────────
    try:
        fig = risk_gauge(result.risk_score, result.risk_category)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    except Exception:
        pass

    # ── CKD Stage badge ───────────────────────────────────────────────────────
    if stage_num in CKD_STAGE_DESC:
        s_label, s_range, s_color = CKD_STAGE_DESC[stage_num]
        sh(f"""
        <div style="background:white;border:1px solid #E2E8F0;border-radius:10px;padding:0.9rem 1.1rem;margin-bottom:0.8rem;">
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <div>
                    <div style="font-size:0.72rem;font-weight:700;color:#64748B;letter-spacing:0.06em;text-transform:uppercase;">CKD Classification</div>
                    <div style="font-size:1.1rem;font-weight:800;color:#0F172A;">Stage {stage_num} — {s_label}</div>
                </div>
                <div style="background:{s_color}15;border:1px solid {s_color}40;border-radius:8px;padding:5px 14px;font-size:0.82rem;font-weight:700;color:{s_color};">eGFR {s_range}</div>
            </div>
        </div>
        """)

    # ── KDIGO G×A Heat Map ────────────────────────────────────────────────────
    _render_kdigo_heatmap(egfr, albumin_label)

    # ── Clinical Interpretation ───────────────────────────────────────────────
    _render_clinical_interpretation(result)

    # ── Contributing factors chart ────────────────────────────────────────────
    if result.contributing_factors:
        factor_scores = {
            f.get("factor", "Unknown"): IMPACT_SCORE.get(f.get("impact", "Moderate"), 8)
            for f in result.contributing_factors
        }
        try:
            fig2 = risk_factor_bar(factor_scores)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        except Exception:
            pass

    # ── Recommendations ───────────────────────────────────────────────────────
    if result.recommendations:
        sh('<div class="section-title"><span>\U0001f4cb</span> Clinical Recommendations</div>')
        for i, rec in enumerate(result.recommendations, 1):
            p_color = "#EF4444" if i <= 2 else ("#F59E0B" if i <= 4 else "#64748B")
            p_label = "HIGH" if i <= 2 else ("MODERATE" if i <= 4 else "ROUTINE")
            sh(f'<div style="background:white;border:1px solid #E2E8F0;border-radius:8px;padding:0.75rem 1rem;margin-bottom:0.4rem;border-left:3px solid {p_color};display:flex;gap:10px;align-items:flex-start;"><div style="background:{p_color}20;color:{p_color};font-size:0.65rem;font-weight:800;padding:2px 7px;border-radius:4px;letter-spacing:0.05em;flex-shrink:0;margin-top:1px;">{p_label}</div><div style="font-size:0.84rem;color:#334155;line-height:1.5;">{rec}</div></div>')

    # ── Evidence Sources ──────────────────────────────────────────────────────
    _render_evidence_sources()


def _render_explainability(factors: list, total_score: float):
    """Horizontal progress bars showing each factor's % contribution to total risk."""
    total_weight = sum(IMPACT_SCORE.get(f.get("impact", "Moderate"), 8) for f in factors)
    if total_weight == 0:
        return

    sh('<div class="rc-card" style="margin-bottom:0.8rem;"><div class="section-title"><span>&#x1f9e0;</span> Risk Score Breakdown <span style="font-size:0.72rem;font-weight:500;color:#64748B;font-style:italic;">(Explainable AI)</span></div>')

    IMPACT_COLORS = {"Low": "#10B981", "Moderate": "#F59E0B", "High": "#EF4444", "Critical": "#7C3AED"}

    for f in factors:
        name   = f.get("factor",  "Unknown")
        value  = f.get("value",   "")
        impact = f.get("impact",  "Moderate")
        detail = f.get("detail",  "")
        weight = IMPACT_SCORE.get(impact, 8)
        pct    = round(weight / total_weight * 100)
        bar_color = IMPACT_COLORS.get(impact, "#64748B")
        sh(f'<div style="margin-bottom:0.7rem;"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;"><div style="font-size:0.82rem;font-weight:600;color:#1E293B;">{name}<span style="font-size:0.75rem;color:#64748B;font-weight:400;margin-left:6px;">({value})</span></div><div style="display:flex;align-items:center;gap:6px;"><span style="font-size:0.72rem;font-weight:700;color:{bar_color};background:{bar_color}18;padding:1px 7px;border-radius:10px;">{impact}</span><span style="font-size:0.78rem;font-weight:700;color:#0F172A;">{pct}%</span></div></div><div style="background:#F1F5F9;border-radius:4px;height:6px;"><div style="background:{bar_color};width:{pct}%;height:6px;border-radius:4px;"></div></div><div style="font-size:0.72rem;color:#94A3B8;margin-top:2px;">{detail}</div></div>')

    sh('</div>')


def _render_kdigo_heatmap(egfr: float, albumin_label: str):
    """KDIGO G×A risk matrix with patient position highlighted."""
    patient_row = _egfr_to_row(float(egfr))
    patient_col = ALBUMIN_COL.get(albumin_label, 0)

    header_style = "font-size:0.72rem;font-weight:700;color:#475569;text-align:center;padding:5px 4px;"
    row_label_style = "font-size:0.72rem;font-weight:700;color:#475569;padding:4px 6px;white-space:nowrap;"

    table_html = '<div class="rc-card" style="margin-bottom:0.8rem;"><div class="section-title"><span>&#x1f5fa;</span> KDIGO G&times;A Risk Classification Matrix</div>'
    table_html += '<table style="width:100%;border-collapse:collapse;font-size:0.75rem;">'
    table_html += f'<tr><th style="{header_style}">GFR Stage</th><th style="{header_style}">eGFR<br>(ml/min)</th><th style="{header_style}">A1<br>&lt;30</th><th style="{header_style}">A2<br>30-300</th><th style="{header_style}">A3<br>&gt;300</th></tr>'

    for r_idx, (stage, egfr_range) in enumerate(GFR_ROWS):
        row_html = f'<tr><td style="{row_label_style}">{stage}</td><td style="{row_label_style}text-align:center;">{egfr_range}</td>'
        for c_idx in range(3):
            bg_c, txt_c, label = KDIGO_MATRIX[r_idx][c_idx]
            is_patient = (r_idx == patient_row and c_idx == patient_col)
            border = "3px solid #0F172A" if is_patient else "1px solid #E2E8F0"
            ring   = "box-shadow:0 0 0 2px white,0 0 0 4px #0F172A;" if is_patient else ""
            pt_badge = ' <span style="font-size:0.6rem;background:white;color:#0F172A;padding:1px 4px;border-radius:4px;font-weight:800;">YOU</span>' if is_patient else ""
            row_html += f'<td style="text-align:center;padding:5px 3px;background:{bg_c};color:{txt_c};font-weight:{"800" if is_patient else "600"};border:{border};{ring}border-radius:4px;">{label}{pt_badge}</td>'
        row_html += '</tr>'
        table_html += row_html

    table_html += '</table>'
    table_html += '<div style="margin-top:0.5rem;font-size:0.72rem;color:#64748B;">Patient position highlighted in black border. Based on KDIGO 2024 CGA classification.</div>'
    table_html += '</div>'
    sh(table_html)


def _render_clinical_interpretation(result):
    """Narrative explanation of why the patient is at their risk level."""
    factors = result.contributing_factors or []
    high_factors = [f.get("factor","") for f in factors if f.get("impact") in ("High","Critical")]
    mod_factors  = [f.get("factor","") for f in factors if f.get("impact") == "Moderate"]

    lines = [f"This patient is classified as <strong>{result.risk_category} Risk</strong> (Score: {result.risk_score:.0f}/100) based on KDIGO 2024 CGA criteria."]
    if high_factors:
        lines.append(f"Primary drivers of elevated risk: <strong>{', '.join(high_factors)}</strong> — each classified as High or Critical impact.")
    if mod_factors:
        lines.append(f"Contributing moderate-impact factors: {', '.join(mod_factors)}.")
    lines.append(f"Assigned CKD Stage <strong>{result.ckd_stage_num}</strong> ({result.egfr_category}). {result.monitoring_priority}.")

    interpretation = " ".join(lines)
    sh(f'<div style="background:linear-gradient(135deg,#EEF2FF,#F0FDF4);border-radius:12px;padding:1rem 1.2rem;margin-bottom:0.8rem;border:1px solid #C7D2FE;"><div style="display:flex;gap:8px;align-items:flex-start;"><span style="font-size:1rem;flex-shrink:0;">&#x1f4cb;</span><div><div style="font-size:0.78rem;font-weight:700;color:#3730A3;margin-bottom:0.4rem;text-transform:uppercase;letter-spacing:0.05em;">Clinical Interpretation</div><div style="font-size:0.84rem;color:#1E293B;line-height:1.65;">{interpretation}</div></div></div></div>')


def _render_evidence_sources():
    sh("""
    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:0.8rem 1rem;margin-top:0.5rem;">
        <div style="font-size:0.72rem;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.5rem;">&#x1f4da; Evidence Sources</div>
        <div style="display:flex;flex-direction:column;gap:4px;">
            <div style="font-size:0.78rem;color:#374151;"><span style="background:#EFF6FF;color:#1D4ED8;font-size:0.65rem;font-weight:700;padding:1px 6px;border-radius:4px;margin-right:5px;">Guideline</span>KDIGO 2024 CKD Clinical Practice Guidelines &mdash; GFR &amp; Albuminuria Categories</div>
            <div style="font-size:0.78rem;color:#374151;"><span style="background:#F0FDF4;color:#065F46;font-size:0.65rem;font-weight:700;padding:1px 6px;border-radius:4px;margin-right:5px;">Guideline</span>ADA Standards of Medical Care in Diabetes 2024 &mdash; Diabetic Kidney Disease</div>
            <div style="font-size:0.78rem;color:#374151;"><span style="background:#FEF3C7;color:#92400E;font-size:0.65rem;font-weight:700;padding:1px 6px;border-radius:4px;margin-right:5px;">Model</span>CKD-EPI 2021 Creatinine Equation &mdash; eGFR Calculation</div>
            <div style="font-size:0.78rem;color:#374151;"><span style="background:#EEF2FF;color:#3730A3;font-size:0.65rem;font-weight:700;padding:1px 6px;border-radius:4px;margin-right:5px;">Systematic Review</span>KDIGO 2020 CGA Heat Map &mdash; Prognosis Classification Matrix</div>
        </div>
    </div>
    """)


def _render_placeholder():
    sh("""
    <div style="background:white;border:2px dashed #E2E8F0;border-radius:16px;padding:3rem;text-align:center;margin-top:0.5rem;">
        <div style="font-size:3rem;margin-bottom:1rem;">&#x2764;&#xfe0f;</div>
        <div style="font-size:1rem;font-weight:700;color:#0F172A;margin-bottom:0.5rem;">Kidney Risk Assessment</div>
        <div style="font-size:0.84rem;color:#64748B;max-width:380px;margin:0 auto;line-height:1.6;">Enter patient demographics, laboratory values, and comorbidities to generate a comprehensive CKD risk stratification with explainable AI scoring and KDIGO heat map.</div>
        <div style="margin-top:1.5rem;display:flex;gap:8px;justify-content:center;flex-wrap:wrap;">
            <span style="background:#FEE2E2;color:#991B1B;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">Explainable Risk Score</span>
            <span style="background:#EFF6FF;color:#1E40AF;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">KDIGO G&times;A Matrix</span>
            <span style="background:#F0FDF4;color:#065F46;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">Clinical Interpretation</span>
        </div>
    </div>
    """)
