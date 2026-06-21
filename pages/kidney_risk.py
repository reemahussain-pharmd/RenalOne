"""Kidney Risk Assessment Page — RenalCare AI."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from models.kidney_risk import RiskInput, calculate_risk
from components.charts import risk_gauge, risk_factor_bar, egfr_trend_placeholder
from utils.helpers import calculate_bmi, classify_bmi


def render():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1e3a5f, #2980b9);
                border-radius: 12px; padding: 1.5rem 2rem; margin-bottom: 1.5rem;'>
        <h2 style='color:white; margin:0; font-size:1.5rem;'>🫀 Kidney Risk Assessment</h2>
        <p style='color:#bde0fe; margin:0.3rem 0 0 0; font-size:0.88rem;'>
            AI-powered CKD risk scoring based on clinical biomarkers and KDIGO guidelines
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='info-box'>
        Complete the clinical assessment form below. All fields are used to generate a personalised
        Kidney Health Score and risk classification. Fields marked with * are required for accurate scoring.
    </div>
    """, unsafe_allow_html=True)

    with st.form("risk_form"):
        # ---- Demographics ----
        st.markdown("<div class='section-header'>👤 Patient Demographics</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.number_input("Age (years)*", min_value=18, max_value=100, value=55, step=1)
            gender = st.selectbox("Gender*", ["Male", "Female"])
        with c2:
            weight = st.number_input("Weight (kg)*", min_value=30.0, max_value=200.0, value=72.0, step=0.5)
            height = st.number_input("Height (cm)*", min_value=120.0, max_value=220.0, value=165.0, step=0.5)
        with c3:
            bmi_calc = calculate_bmi(weight, height)
            bmi_cat, bmi_col = classify_bmi(bmi_calc)
            st.metric("Calculated BMI", f"{bmi_calc}", f"{bmi_cat}")
            st.markdown(f"<span style='color:{bmi_col}; font-size:0.8rem;'>●</span> {bmi_cat}", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ---- Comorbidities ----
        st.markdown("<div class='section-header'>🏥 Comorbidities & Risk Factors</div>", unsafe_allow_html=True)
        c4, c5 = st.columns(2)
        with c4:
            diabetes = st.checkbox("Diabetes Mellitus", value=True)
            hypertension = st.checkbox("Hypertension", value=True)
            smoking = st.checkbox("Active Smoking", value=False)
        with c5:
            alcohol = st.checkbox("Alcohol Use", value=False)
            family_history = st.checkbox("Family History of CKD/Kidney Disease", value=False)

        # BP fields
        st.markdown("<br>", unsafe_allow_html=True)
        bp_c1, bp_c2, hba1c_c = st.columns(3)
        with bp_c1:
            systolic_bp = st.number_input("Systolic BP (mmHg)", min_value=80, max_value=250, value=145, step=1)
        with bp_c2:
            diastolic_bp = st.number_input("Diastolic BP (mmHg)", min_value=40, max_value=150, value=90, step=1)
        with hba1c_c:
            hba1c = st.number_input("HbA1c (%)", min_value=4.0, max_value=20.0, value=8.2, step=0.1,
                                    help="Glycated haemoglobin — leave at 0 if not diabetic or unavailable")

        st.markdown("<br>", unsafe_allow_html=True)

        # ---- Lab Values ----
        st.markdown("<div class='section-header'>🧪 Laboratory Values</div>", unsafe_allow_html=True)
        l1, l2, l3 = st.columns(3)
        with l1:
            creatinine = st.number_input("Serum Creatinine (mg/dL)*", min_value=0.3, max_value=20.0,
                                          value=2.1, step=0.1)
        with l2:
            egfr = st.number_input("eGFR (mL/min/1.73m²)*", min_value=1.0, max_value=120.0,
                                    value=35.0, step=0.5,
                                    help="Use CKD-EPI 2021 equation. eGFR calculators available at mdcalc.com")
        with l3:
            albuminuria = st.selectbox("Albuminuria*", ["None", "Microalbuminuria", "Macroalbuminuria"],
                                       help="Microalbuminuria: 30-300 mg/g; Macroalbuminuria: >300 mg/g")

        st.markdown("<br>", unsafe_allow_html=True)

        submit = st.form_submit_button("🔍 Analyse Kidney Risk", use_container_width=True)

    if submit:
        with st.spinner("Running clinical risk analysis..."):
            inp = RiskInput(
                age=age, gender=gender, weight_kg=weight, height_cm=height, bmi=bmi_calc,
                diabetes=diabetes, hypertension=hypertension, smoking=smoking, alcohol=alcohol,
                family_history=family_history,
                serum_creatinine=creatinine, egfr=egfr, albuminuria=albuminuria,
                hba1c=hba1c if hba1c > 4.0 else None,
                systolic_bp=systolic_bp, diastolic_bp=diastolic_bp,
            )
            result = calculate_risk(inp)

        # Save to session
        st.session_state["risk_result"] = result
        st.session_state["risk_input"] = inp

        # ---- Results ----
        st.markdown("---")
        st.markdown("## 📊 Risk Assessment Results")

        # Top metrics
        cat = result.risk_category
        badge_class = {"Low": "badge-low", "Moderate": "badge-mod", "High": "badge-high", "Critical": "badge-crit"}.get(cat, "badge-mod")
        risk_icon = {"Low": "✅", "Moderate": "⚠️", "High": "🔶", "Critical": "🚨"}.get(cat, "⚠️")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class='metric-card' style='border-left-color: #27ae60;'>
                <p>Kidney Health Score</p>
                <h3 style='color:#27ae60;'>{result.kidney_health_score}</h3>
                <span style='font-size:0.75rem; color:#718096;'>out of 100</span>
            </div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class='metric-card' style='border-left-color: #e74c3c;'>
                <p>Risk Score</p>
                <h3 style='color:#e74c3c;'>{result.risk_score}</h3>
                <span style='font-size:0.75rem; color:#718096;'>out of 100</span>
            </div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class='metric-card'>
                <p>Risk Classification</p>
                <h3 style='font-size:1.3rem;'>{risk_icon} {cat}</h3>
                <span class='{badge_class}'>{cat}</span>
            </div>""", unsafe_allow_html=True)
        with m4:
            st.markdown(f"""
            <div class='metric-card'>
                <p>CKD Stage</p>
                <h3 style='font-size:1.2rem;'>{result.ckd_stage_num}</h3>
                <span style='font-size:0.75rem; color:#718096;'>{result.egfr_category}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Charts row
        ch1, ch2 = st.columns([1, 1])
        with ch1:
            st.plotly_chart(risk_gauge(result.risk_score, "Kidney Risk Score"), use_container_width=True)
        with ch2:
            st.plotly_chart(risk_gauge(100 - result.kidney_health_score, "Health Burden"), use_container_width=True)

        # CKD Stage card
        stage_colors = {
            "G1": "#27ae60", "G2": "#2ecc71", "G3a": "#f39c12",
            "G3b": "#e67e22", "G4": "#e74c3c", "G5": "#8e44ad",
        }
        stage_color = stage_colors.get(result.ckd_stage_num, "#2980b9")
        st.markdown(f"""
        <div style='background:{stage_color}22; border:2px solid {stage_color}; border-radius:10px;
                    padding:1rem 1.5rem; margin:0.5rem 0;'>
            <div style='font-size:0.8rem; color:#4a5568; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;'>
                CKD Classification
            </div>
            <div style='font-size:1.5rem; font-weight:700; color:{stage_color};'>{result.ckd_stage}</div>
            <div style='font-size:0.85rem; color:#4a5568;'>eGFR: {egfr:.1f} mL/min/1.73m² — {result.egfr_category}</div>
        </div>
        """, unsafe_allow_html=True)

        # Clinical summary
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📝 Clinical Summary")
        st.markdown(f"""
        <div style='background:white; border-radius:10px; padding:1.2rem; box-shadow:0 2px 8px rgba(0,0,0,0.06);
                    border-left:4px solid {stage_color};'>
            {result.clinical_summary}
        </div>
        """, unsafe_allow_html=True)

        # Contributing factors
        if result.contributing_factors:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### ⚡ Contributing Risk Factors")
            st.plotly_chart(risk_factor_bar(result.contributing_factors), use_container_width=True)

            for factor in result.contributing_factors:
                impact = factor.get("impact", "Low")
                impact_color = {"High": "#e74c3c", "Moderate": "#f39c12", "Low": "#3498db", "Critical": "#8e44ad"}.get(impact, "#95a5a6")
                st.markdown(f"""
                <div style='background:white; border-radius:8px; padding:0.7rem 1rem; margin-bottom:0.4rem;
                            box-shadow:0 1px 4px rgba(0,0,0,0.06); border-left:3px solid {impact_color};
                            display:flex; align-items:center; gap:1rem;'>
                    <div style='flex:1;'>
                        <span style='font-weight:600; color:#1e3a5f;'>{factor["factor"]}</span>
                        <span style='color:#718096; font-size:0.85rem; margin-left:0.5rem;'>— {factor.get("value","")}</span>
                    </div>
                    <span style='background:{impact_color}22; color:{impact_color}; padding:2px 10px;
                                 border-radius:12px; font-size:0.78rem; font-weight:600;'>{impact}</span>
                </div>
                """, unsafe_allow_html=True)
                if factor.get("detail"):
                    st.markdown(f"<div style='font-size:0.8rem; color:#718096; margin:-0.2rem 0 0.4rem 1rem;'>{factor['detail']}</div>", unsafe_allow_html=True)

        # Recommendations
        if result.recommendations:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 🎯 Clinical Recommendations")
            st.markdown(f"""
            <div style='background:#fffaf0; border:1px solid #fbd38d; border-radius:10px; padding:1rem 1.2rem;'>
                <div style='font-weight:600; color:#d69e2e; margin-bottom:0.5rem;'>
                    ⚠️ {result.monitoring_priority}
                </div>
            </div>
            """, unsafe_allow_html=True)
            for i, rec in enumerate(result.recommendations, 1):
                st.markdown(f"""
                <div style='background:white; border-radius:8px; padding:0.6rem 1rem; margin:0.3rem 0;
                            box-shadow:0 1px 4px rgba(0,0,0,0.05); display:flex; gap:0.8rem; align-items:flex-start;'>
                    <span style='background:#2980b9; color:white; border-radius:50%; width:20px; height:20px;
                                 display:flex; align-items:center; justify-content:center; font-size:0.7rem;
                                 font-weight:700; flex-shrink:0;'>{i}</span>
                    <span style='font-size:0.87rem; color:#2d3748;'>{rec}</span>
                </div>
                """, unsafe_allow_html=True)

        # eGFR trend
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📈 eGFR Reference Trend")
        st.plotly_chart(egfr_trend_placeholder(), use_container_width=True)
        st.caption("Sample eGFR trend for reference. Connect to longitudinal patient data for personalised trend analysis.")

        # Navigate to report
        st.markdown("---")
        st.markdown("""
        <div class='success-box'>
            ✅ Risk assessment complete. Navigate to <b>Report Generator</b> to include this analysis in a full clinical PDF report.
        </div>
        """, unsafe_allow_html=True)

        if st.button("📋 Generate Clinical Report →", use_container_width=True):
            st.session_state.current_page = "Report"
            st.rerun()
    else:
        # Placeholder state
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background:white; border-radius:12px; padding:3rem; text-align:center;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
            <div style='font-size:3rem; margin-bottom:1rem;'>🫀</div>
            <h3 style='color:#1e3a5f;'>Complete the Assessment Form</h3>
            <p style='color:#718096; font-size:0.9rem;'>
                Fill in the clinical parameters above and click <b>Analyse Kidney Risk</b>
                to generate an AI-powered kidney risk assessment.
            </p>
        </div>
        """, unsafe_allow_html=True)
