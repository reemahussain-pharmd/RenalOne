"""Medication Intelligence Engine Page — RenalCare OS."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from medication.checker import MedicationInput, run_medication_review


COMMON_MEDS = [
    "Metformin", "Insulin", "Amlodipine", "Lisinopril", "Losartan",
    "Furosemide", "Spironolactone", "Ibuprofen", "Aspirin",
    "Atorvastatin", "Rosuvastatin", "Omeprazole", "Pantoprazole",
    "Ferrous Sulphate", "Calcitriol", "Cinacalcet", "Sevelamer",
    "Erythropoietin", "Darbepoetin", "Digoxin", "Atenolol",
    "Carvedilol", "Gabapentin", "Pregabalin", "Allopurinol",
    "Tramadol", "Paracetamol", "Clopidogrel", "Warfarin",
]

COMMON_DIAGNOSES = [
    "CKD Stage 3", "CKD Stage 4", "CKD Stage 5 (ESRD)",
    "Type 2 Diabetes Mellitus", "Hypertension", "Heart Failure",
    "Anaemia of CKD", "CKD-Mineral Bone Disorder", "Hyperkalemia",
    "Hyperuricaemia/Gout", "Coronary Artery Disease",
]


def _severity_badge(severity: str) -> str:
    colors = {"High": ("#e74c3c", "#fdedec"), "Moderate": ("#e67e22", "#fdf2e9"), "Low": ("#3498db", "#ebf5fb")}
    c, bg = colors.get(severity, ("#718096", "#f8f9fa"))
    return f"<span style='background:{bg}; color:{c}; padding:2px 10px; border-radius:12px; font-size:0.78rem; font-weight:600;'>{severity}</span>"


def _flag_type_icon(flag_type: str) -> str:
    icons = {
        "Nephrotoxicity": "🫘",
        "Dose Adjustment": "⚖️",
        "Interaction": "🔗",
        "ADR": "⚠️",
        "Monitoring": "🔍",
    }
    return icons.get(flag_type, "⚠️")


def render():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #4a0e7a, #8e44ad);
                border-radius: 12px; padding: 1.5rem 2rem; margin-bottom: 1.5rem;'>
        <h2 style='color:white; margin:0; font-size:1.5rem;'>💊 Medication Intelligence Engine</h2>
        <p style='color:#d7bdf7; margin:0.3rem 0 0 0; font-size:0.88rem;'>
            Clinical Pharmacy AI · Drug Safety Screening · PharmD Intelligence Module
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='warning-box'>
        <b>⚕️ Clinical Disclaimer:</b> This AI-generated medication review is for <b>clinical decision support only</b>.
        It does not replace the judgment of a licensed pharmacist or physician.
        All medication decisions must be made by qualified healthcare professionals.
    </div>
    """, unsafe_allow_html=True)

    with st.form("med_form"):
        st.markdown("<div class='section-header'>🏥 Patient Diagnoses</div>", unsafe_allow_html=True)
        diagnoses_selected = st.multiselect(
            "Select current diagnoses",
            options=COMMON_DIAGNOSES,
            default=["CKD Stage 4", "Type 2 Diabetes Mellitus", "Hypertension"],
        )
        extra_dx = st.text_input("Additional diagnoses (comma separated)", placeholder="e.g. Diabetic Nephropathy, Gout")
        if extra_dx:
            diagnoses_selected += [d.strip() for d in extra_dx.split(",") if d.strip()]

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>💊 Current Medications</div>", unsafe_allow_html=True)
        meds_selected = st.multiselect(
            "Select current medications",
            options=COMMON_MEDS,
            default=["Metformin", "Ibuprofen", "Lisinopril", "Furosemide"],
        )
        extra_meds = st.text_input("Additional medications (comma separated)", placeholder="e.g. Cinacalcet 30mg, Sevelamer 800mg")
        if extra_meds:
            meds_selected += [m.strip() for m in extra_meds.split(",") if m.strip()]

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>🧪 Laboratory Values</div>", unsafe_allow_html=True)
        l1, l2, l3, l4 = st.columns(4)
        with l1:
            egfr = st.number_input("eGFR (mL/min/1.73m²)", min_value=1.0, max_value=120.0, value=28.0, step=0.5)
        with l2:
            creatinine = st.number_input("Serum Creatinine (mg/dL)", min_value=0.3, max_value=20.0, value=2.8, step=0.1)
        with l3:
            potassium = st.number_input("Potassium (mEq/L)", min_value=2.0, max_value=8.0, value=5.2, step=0.1)
        with l4:
            hemoglobin = st.number_input("Hemoglobin (g/dL)", min_value=4.0, max_value=18.0, value=9.5, step=0.1)

        ckd_stage = st.selectbox("CKD Stage", ["G1", "G2", "G3a", "G3b", "G4", "G5 (ESRD)"], index=4)

        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("🔍 Run Medication Review", use_container_width=True)

    if submit:
        if not meds_selected:
            st.error("Please select at least one medication to review.")
            return
        if not diagnoses_selected:
            st.warning("Please select at least one diagnosis for contextual analysis.")

        with st.spinner("Running Clinical Pharmacy AI analysis..."):
            inp = MedicationInput(
                medications=meds_selected,
                diagnoses=diagnoses_selected,
                egfr=egfr,
                serum_creatinine=creatinine,
                potassium=potassium,
                hemoglobin=hemoglobin,
                ckd_stage=ckd_stage,
            )
            result = run_medication_review(inp)

        # Save to session
        st.session_state["medication_result"] = result
        st.session_state["medication_input"] = inp

        st.markdown("---")
        st.markdown("## 📋 Medication Review Report")

        # Overall risk banner
        risk_configs = {
            "Low": ("✅", "#27ae60", "#d5f5e3"),
            "Moderate": ("⚠️", "#e67e22", "#fdf2e9"),
            "High": ("🔶", "#e74c3c", "#fdedec"),
            "Critical": ("🚨", "#c0392b", "#fdedec"),
        }
        icon, color, bg = risk_configs.get(result.overall_risk, ("ℹ️", "#2980b9", "#ebf5fb"))
        st.markdown(f"""
        <div style='background:{bg}; border:2px solid {color}; border-radius:10px; padding:1rem 1.5rem; margin-bottom:1rem;'>
            <span style='font-size:1.1rem; font-weight:700; color:{color};'>{icon} Overall Medication Risk: {result.overall_risk}</span>
            <br><span style='font-size:0.85rem; color:#4a5568;'>
                {len(result.flags)} flag(s) identified across {len(meds_selected)} medication(s)
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Medication list
        st.markdown("### 💊 Reviewed Medications")
        med_cols = st.columns(min(len(meds_selected), 4))
        for i, med in enumerate(meds_selected):
            with med_cols[i % len(med_cols)]:
                flagged = any(med.lower() in f.drug.lower() for f in result.flags)
                card_color = "#e74c3c" if flagged else "#27ae60"
                card_bg = "#fff5f5" if flagged else "#f0fff4"
                flag_text = "⚠️ Flagged" if flagged else "✅ No flags"
                st.markdown(f"""
                <div style='background:{card_bg}; border:1px solid {card_color}33; border-radius:8px;
                            padding:0.6rem 0.8rem; margin-bottom:0.4rem; border-left:3px solid {card_color};'>
                    <div style='font-weight:600; font-size:0.85rem; color:#1e3a5f;'>{med}</div>
                    <div style='font-size:0.75rem; color:{card_color};'>{flag_text}</div>
                </div>
                """, unsafe_allow_html=True)

        # Flags
        if result.flags:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 🚨 Drug Safety Flags")
            for flag in result.flags:
                sev = flag.severity
                sev_colors = {"High": ("#e74c3c", "#fff5f5"), "Moderate": ("#e67e22", "#fffaf0"), "Low": ("#3498db", "#ebf5fb")}
                fc, fbg = sev_colors.get(sev, ("#718096", "#f8f9fa"))
                st.markdown(f"""
                <div style='background:{fbg}; border:1px solid {fc}44; border-radius:10px; padding:1rem 1.2rem;
                            margin-bottom:0.6rem; border-left:4px solid {fc};'>
                    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;'>
                        <span style='font-weight:700; color:#1e3a5f; font-size:0.95rem;'>
                            {_flag_type_icon(flag.flag_type)} {flag.drug}
                        </span>
                        <div style='display:flex; gap:0.5rem;'>
                            <span style='background:#e8eaf6; color:#3f51b5; padding:2px 8px; border-radius:10px; font-size:0.75rem;'>{flag.flag_type}</span>
                            {_severity_badge(flag.severity)}
                        </div>
                    </div>
                    <div style='font-size:0.85rem; color:#4a5568; margin-bottom:0.3rem;'><b>Concern:</b> {flag.detail}</div>
                    <div style='font-size:0.85rem; color:{fc};'><b>Recommended Action:</b> {flag.action}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='success-box'>
                ✅ No major drug safety flags identified by rule-based screening.
                A comprehensive clinical pharmacist review is still recommended.
            </div>
            """, unsafe_allow_html=True)

        # Monitoring requirements
        if result.monitoring_requirements:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 🔍 Monitoring Requirements")
            for req in result.monitoring_requirements:
                st.markdown(f"""
                <div style='background:white; border-radius:8px; padding:0.6rem 1rem; margin:0.3rem 0;
                            box-shadow:0 1px 4px rgba(0,0,0,0.05); border-left:3px solid #2980b9;
                            font-size:0.87rem; color:#2d3748;'>
                    🔍 {req}
                </div>
                """, unsafe_allow_html=True)

        # AI narrative
        if result.ai_narrative:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 🤖 Clinical Pharmacist AI Review")
            st.markdown(f"""
            <div style='background:white; border-radius:10px; padding:1.5rem; box-shadow:0 2px 8px rgba(0,0,0,0.06);
                        border-left:4px solid #8e44ad;'>
            """, unsafe_allow_html=True)
            st.markdown(result.ai_narrative)
            st.markdown("</div>", unsafe_allow_html=True)

        # Clinical considerations
        if result.clinical_considerations:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 💡 Clinical Considerations")
            for con in result.clinical_considerations:
                st.markdown(f"""
                <div style='background:#f8f9fa; border-radius:6px; padding:0.5rem 1rem; margin:0.2rem 0;
                            font-size:0.85rem; color:#4a5568; border-left:3px solid #9b59b6;'>
                    {con}
                </div>
                """, unsafe_allow_html=True)

        # Disclaimer
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='warning-box' style='font-size:0.82rem;'>
            {result.disclaimer}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("📋 Add to Clinical Report →", use_container_width=True):
            st.session_state.current_page = "Report"
            st.rerun()

    elif not submit:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background:white; border-radius:12px; padding:3rem; text-align:center;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
            <div style='font-size:3rem; margin-bottom:1rem;'>💊</div>
            <h3 style='color:#1e3a5f;'>PharmD AI Medication Review</h3>
            <p style='color:#718096; font-size:0.9rem;'>
                Select diagnoses, medications, and lab values above to run an
                AI-powered medication safety review for CKD patients.
            </p>
            <div style='display:flex; flex-wrap:wrap; gap:0.5rem; justify-content:center; margin-top:1rem;'>
                <span style='background:#f3e8ff; color:#8e44ad; padding:4px 12px; border-radius:12px; font-size:0.8rem;'>Drug Interactions</span>
                <span style='background:#f3e8ff; color:#8e44ad; padding:4px 12px; border-radius:12px; font-size:0.8rem;'>Nephrotoxicity</span>
                <span style='background:#f3e8ff; color:#8e44ad; padding:4px 12px; border-radius:12px; font-size:0.8rem;'>Dose Adjustment</span>
                <span style='background:#f3e8ff; color:#8e44ad; padding:4px 12px; border-radius:12px; font-size:0.8rem;'>ADR Risk</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
