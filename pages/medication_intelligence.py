"""Medication Intelligence Engine Page — RenalCare AI."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from components.styles import sh
from medication.checker import MedicationInput, run_medication_review
from utils.constants import COMMON_DIAGNOSES, COMMON_MEDICATIONS


SEVERITY_CONFIG = {
    "HIGH":     ("#EF4444", "#FEE2E2", "#991B1B", "\U0001f534"),
    "MODERATE": ("#F59E0B", "#FEF3C7", "#92400E", "\U0001f7e1"),
    "LOW":      ("#3B82F6", "#EFF6FF", "#1E40AF", "\U0001f535"),
    "INFO":     ("#6366F1", "#EEF2FF", "#3730A3", "\U0001f7e3"),
}


def render():
    # ── Page Header ────────────────────────────────────────────────────────
    sh("""
    <div class="page-header">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;">
            <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.5rem;">
                    <span style="font-size:1.6rem;">\U0001f48a</span>
                    <span style="background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.9);
                                 font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:20px;
                                 letter-spacing:0.06em;">PHARMD SIGNATURE MODULE</span>
                </div>
                <h1 style="color:white !important;font-size:1.7rem !important;font-weight:800 !important;
                           margin:0 0 0.3rem 0 !important;letter-spacing:-0.02em;">
                    Medication Intelligence Engine
                </h1>
                <p style="color:rgba(255,255,255,0.72) !important;font-size:0.88rem !important;margin:0 !important;">
                    Nephrotoxicity screening &bull; Renal dose adjustment &bull; Drug interaction analysis
                </p>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.7rem;color:rgba(255,255,255,0.5);text-transform:uppercase;
                            letter-spacing:0.07em;">Evidence Base</div>
                <div style="font-size:0.85rem;color:rgba(255,255,255,0.85);font-weight:600;">KDIGO 2024</div>
                <div style="font-size:0.85rem;color:rgba(255,255,255,0.85);font-weight:600;">Micromedex</div>
            </div>
        </div>
    </div>
    """)

    left_col, right_col = st.columns([1.1, 1.5])

    with left_col:
        with st.form("med_form"):
            sh('<div class="section-title-accent"><span>\U0001f9fe</span> Patient Profile</div>')

            egfr = st.number_input(
                "eGFR (mL/min/1.73m²)",
                min_value=1, max_value=150, value=45,
                help="CKD-EPI calculated eGFR"
            )
            creatinine = st.number_input("Serum Creatinine (mg/dL)", 0.4, 15.0, 1.8, 0.1)

            sh('<div style="font-size:0.83rem;font-weight:600;color:#374151;margin:0.8rem 0 0.3rem;">Active Diagnoses</div>')
            diagnoses = st.multiselect(
                "Diagnoses",
                options=COMMON_DIAGNOSES,
                default=["Chronic Kidney Disease", "Hypertension"],
                label_visibility="collapsed",
            )

            sh('<div style="font-size:0.83rem;font-weight:600;color:#374151;margin:0.8rem 0 0.3rem;">Current Medications</div>')
            medications = st.multiselect(
                "Medications",
                options=COMMON_MEDICATIONS,
                default=["Metformin", "Ibuprofen", "Lisinopril"],
                label_visibility="collapsed",
            )

            sh("**Laboratory Values**")
            c1, c2 = st.columns(2)
            with c1:
                potassium = st.number_input("Potassium (mEq/L)", 2.5, 7.0, 4.2, 0.1)
            with c2:
                sodium = st.number_input("Sodium (mEq/L)", 120, 160, 138)
            hemoglobin = st.number_input("Hemoglobin (g/dL)", 5.0, 18.0, 10.5, 0.1)

            submitted = st.form_submit_button(
                "\U0001f50d  Run Medication Review",
                use_container_width=True,
                type="primary",
            )

    with right_col:
        if submitted and medications:
            with st.spinner("Analyzing medications..."):
                inp = MedicationInput(
                    egfr=float(egfr),
                    serum_creatinine=float(creatinine),
                    diagnoses=diagnoses,
                    medications=medications,
                    potassium=potassium,
                    sodium=sodium,
                    hemoglobin=hemoglobin,
                )
                result = run_medication_review(inp)
                st.session_state.med_result = result
                st.session_state.med_input_count = len(medications)

        if st.session_state.get("med_result"):
            result = st.session_state.med_result
            med_count = st.session_state.get("med_input_count", len(medications) if submitted else 0)
            _render_results(result, med_count)
        elif submitted and not medications:
            st.markdown("""
            <div class="alert alert-warning">
                ⚠️ Please select at least one medication to review.
            </div>
            """)
        else:
            _render_placeholder()


def _render_results(result, med_count=0):
    # Determine counts
    flags = result.flags
    high_flags = [f for f in flags if f.severity.upper() == "HIGH"]
    mod_flags  = [f for f in flags if f.severity.upper() == "MODERATE"]
    low_flags  = [f for f in flags if f.severity.upper() not in ("HIGH", "MODERATE")]
    total = len(flags)
    critical_count = len(high_flags)

    risk_color = "#EF4444" if critical_count > 0 else ("#F59E0B" if mod_flags else "#10B981")
    risk_label = "HIGH RISK" if critical_count > 0 else ("MODERATE RISK" if mod_flags else "LOW RISK")
    risk_bg    = "#FEE2E2" if critical_count > 0 else ("#FEF3C7" if mod_flags else "#D1FAE5")

    sh(f"""
    <div style="background:{risk_bg};border:2px solid {risk_color};border-radius:14px;
                padding:1.2rem 1.5rem;margin-bottom:1.2rem;
                display:flex;align-items:center;justify-content:space-between;">
        <div>
            <div style="font-size:0.72rem;font-weight:700;color:{risk_color};
                        letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.2rem;">
                Medication Review Complete
            </div>
            <div style="font-size:1.4rem;font-weight:800;color:{risk_color};">{risk_label}</div>
            <div style="font-size:0.82rem;color:#334155;margin-top:0.2rem;">
                {total} flags identified &bull; {med_count} medications reviewed
            </div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:2rem;font-weight:900;color:{risk_color};">{critical_count}</div>
            <div style="font-size:0.72rem;font-weight:700;color:{risk_color};
                        letter-spacing:0.06em;text-transform:uppercase;">Critical Alerts</div>
        </div>
    </div>
    """)

    # ── Severity pills ─────────────────────────────────────────────────────
    sh(f"""
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:1rem;">
        <span style="background:#FEE2E2;color:#991B1B;padding:4px 12px;border-radius:20px;
                     font-size:0.77rem;font-weight:700;">
            \U0001f534 {len(high_flags)} High Severity
        </span>
        <span style="background:#FEF3C7;color:#92400E;padding:4px 12px;border-radius:20px;
                     font-size:0.77rem;font-weight:700;">
            \U0001f7e1 {len(mod_flags)} Moderate
        </span>
        <span style="background:#EFF6FF;color:#1E40AF;padding:4px 12px;border-radius:20px;
                     font-size:0.77rem;font-weight:700;">
            \U0001f535 {len(low_flags)} Informational
        </span>
    </div>
    """)

    # ── Drug flag cards ────────────────────────────────────────────────────
    if flags:
        sh('<div class="section-title"><span>\U0001f6a8</span> Drug Alerts</div>')
        for flag in flags:
            sev = flag.severity.upper()
            color, bg, text_color, dot = SEVERITY_CONFIG.get(sev, SEVERITY_CONFIG["INFO"])
            sh(f"""
            <div class="flag-card" style="border-left:4px solid {color};background:{bg}18;">
                <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:8px;">
                    <div style="flex:1;">
                        <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.35rem;">
                            <span style="font-size:1rem;">{dot}</span>
                            <span style="font-size:0.9rem;font-weight:700;color:#0F172A;">{flag.drug}</span>
                            <span style="background:{bg};color:{text_color};font-size:0.68rem;
                                         font-weight:700;padding:2px 8px;border-radius:20px;
                                         letter-spacing:0.05em;border:1px solid {color}40;">
                                {flag.flag_type.replace('_', ' ')}
                            </span>
                        </div>
                        <div style="font-size:0.83rem;color:#374151;line-height:1.5;margin-bottom:0.5rem;">
                            {flag.detail}
                        </div>
                        <div style="background:rgba(255,255,255,0.7);border-radius:6px;
                                    padding:6px 10px;font-size:0.8rem;color:#1E3A5F;font-weight:500;">
                            \U0001f4a1 <strong>Action:</strong> {flag.action}
                        </div>
                    </div>
                    <div style="background:{color};color:white;border-radius:6px;padding:4px 9px;
                                font-size:0.68rem;font-weight:700;letter-spacing:0.04em;
                                white-space:nowrap;flex-shrink:0;align-self:flex-start;">
                        {sev}
                    </div>
                </div>
            </div>
            """)
    else:
        sh("""
        <div class="alert alert-success">
            ✅ <strong>No drug alerts identified.</strong> All selected medications appear
            appropriate for the entered eGFR and clinical context.
        </div>
        """)

    # ── Monitoring requirements ────────────────────────────────────────────
    monitoring = getattr(result, "monitoring_requirements", [])
    if monitoring:
        sh("<div style='margin-top:0.8rem;'></div>")
        sh('<div class="section-title"><span>\U0001f9ea</span> Monitoring Requirements</div>')
        mon_html = '<div style="display:flex;flex-wrap:wrap;gap:6px;">'
        for m in monitoring:
            mon_html += f'<span style="background:#EEF2FF;color:#3730A3;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">\U0001f4dd {m}</span>'
        mon_html += '</div>'
        sh(mon_html)

    # ── AI narrative ───────────────────────────────────────────────────────
    if result.ai_narrative:
        sh("<div style='margin-top:0.8rem;'></div>")
        sh(f"""
        <div style="background:linear-gradient(135deg,#EEF2FF,#F0FDF4);border-radius:12px;
                    padding:1.2rem;border:1px solid #C7D2FE;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.7rem;">
                <span style="font-size:1.1rem;">\U0001f916</span>
                <span style="font-size:0.85rem;font-weight:700;color:#3730A3;">AI Clinical Narrative</span>
                <span style="background:#EEF2FF;color:#6366F1;font-size:0.68rem;font-weight:700;
                             padding:2px 8px;border-radius:20px;letter-spacing:0.05em;">GPT-4o</span>
            </div>
            <div style="font-size:0.85rem;color:#1E293B;line-height:1.65;">
                {result.ai_narrative.replace(chr(10), '<br>')}
            </div>
        </div>
        """)


def _render_placeholder():
    sh("""
    <div style="background:white;border:2px dashed #E2E8F0;border-radius:16px;
                padding:3rem;text-align:center;">
        <div style="font-size:3rem;margin-bottom:1rem;">\U0001f48a</div>
        <div style="font-size:1rem;font-weight:700;color:#0F172A;margin-bottom:0.5rem;">
            Medication Intelligence Engine
        </div>
        <div style="font-size:0.84rem;color:#64748B;max-width:380px;margin:0 auto;line-height:1.6;">
            Complete the patient profile form to run a comprehensive medication safety
            review including nephrotoxicity screening, dose adjustment requirements,
            and drug interaction analysis.
        </div>
        <div style="margin-top:1.5rem;display:flex;gap:8px;justify-content:center;flex-wrap:wrap;">
            <span style="background:#EEF2FF;color:#3730A3;font-size:0.78rem;font-weight:600;
                         padding:5px 12px;border-radius:8px;">Nephrotoxicity Check</span>
            <span style="background:#FEF3C7;color:#92400E;font-size:0.78rem;font-weight:600;
                         padding:5px 12px;border-radius:8px;">Renal Dose Adjustment</span>
            <span style="background:#FEE2E2;color:#991B1B;font-size:0.78rem;font-weight:600;
                         padding:5px 12px;border-radius:8px;">Drug Interactions</span>
        </div>
    </div>
    """)
