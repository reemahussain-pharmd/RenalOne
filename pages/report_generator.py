"""AI Renal Report Generator Page â€” RenalCare AI."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from datetime import datetime
from reports.generator import generate_report, REPORTLAB_AVAILABLE
from dataclasses import asdict


def _to_dict(obj):
    """Convert dataclass or plain dict to dict safely."""
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    try:
        return asdict(obj)
    except Exception:
        return obj.__dict__ if hasattr(obj, "__dict__") else {}


def render():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #7b0000, #c0392b);
                border-radius: 12px; padding: 1.5rem 2rem; margin-bottom: 1.5rem;'>
        <h2 style='color:white; margin:0; font-size:1.5rem;'>ðŸ“‹ AI Renal Report Generator</h2>
        <p style='color:#fadbd8; margin:0.3rem 0 0 0; font-size:0.88rem;'>
            Generate comprehensive, professional-grade PDF clinical reports
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not REPORTLAB_AVAILABLE:
        st.warning("âš ï¸ ReportLab is not installed. Install it with: `pip install reportlab`")

    # Session data status
    has_risk = "risk_result" in st.session_state
    has_med = "medication_result" in st.session_state
    has_econ = "economic_result" in st.session_state

    st.markdown("### ðŸ“Š Available Data")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        if has_risk:
            r = st.session_state["risk_result"]
            st.markdown(f"""
            <div class='success-box'>
                âœ… <b>Kidney Risk Assessment</b><br>
                <span style='font-size:0.82rem;'>Risk: {r.risk_category} Â· Score: {r.risk_score}/100 Â· {r.ckd_stage}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='warning-box'>
                âš ï¸ <b>Kidney Risk Assessment</b><br>
                <span style='font-size:0.82rem;'>Not completed â€” go to Kidney Risk page</span>
            </div>
            """, unsafe_allow_html=True)
    with sc2:
        if has_med:
            m = st.session_state["medication_result"]
            st.markdown(f"""
            <div class='success-box'>
                âœ… <b>Medication Review</b><br>
                <span style='font-size:0.82rem;'>Overall Risk: {m.overall_risk} Â· {len(m.flags)} flag(s)</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='warning-box'>
                âš ï¸ <b>Medication Review</b><br>
                <span style='font-size:0.82rem;'>Not completed â€” go to Medication page</span>
            </div>
            """, unsafe_allow_html=True)
    with sc3:
        if has_econ:
            e = st.session_state["economic_result"]
            st.markdown(f"""
            <div class='success-box'>
                âœ… <b>Economic Analysis</b><br>
                <span style='font-size:0.82rem;'>Annual: â‚¹{e.total_annual:,.0f} Â· {e.financial_risk_category} Risk</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='warning-box'>
                âš ï¸ <b>Economic Analysis</b><br>
                <span style='font-size:0.82rem;'>Not completed â€” go to Pharmacoeconomics page</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### âš™ï¸ Report Configuration")

    with st.form("report_form"):
        r1, r2, r3 = st.columns(3)
        with r1:
            patient_name = st.text_input("Patient Name / ID", value="Patient Demo", placeholder="Enter patient name or anonymous ID")
        with r2:
            patient_age = st.number_input("Age (years)", min_value=18, max_value=100, value=55)
        with r3:
            patient_gender = st.selectbox("Gender", ["Male", "Female", "Other"])

        report_date = st.date_input("Report Date", value=datetime.now())
        report_type = st.selectbox("Report Type", ["Clinical Report (Doctor)", "Patient Summary", "Research Report"])

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Include Sections:**")
        inc1, inc2, inc3 = st.columns(3)
        with inc1:
            include_risk = st.checkbox("Kidney Risk Analysis", value=has_risk)
            include_med = st.checkbox("Medication Review", value=has_med)
        with inc2:
            include_econ = st.checkbox("Economic Analysis", value=has_econ)
            include_nutrition = st.checkbox("Nutrition Notes", value=False)
        with inc3:
            include_evidence = st.checkbox("Evidence Summary", value=False)

        clinical_notes = st.text_area(
            "Clinical Notes (optional)",
            placeholder="Enter additional clinical observations, treatment plans, or notes for this patient report...",
            height=100,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        gen_btn = st.form_submit_button("ðŸ“‹ Generate PDF Report", use_container_width=True)

    if gen_btn:
        # Build report data
        report_data = {
            "patient_name": patient_name or "Anonymous",
            "patient_age": patient_age,
            "patient_gender": patient_gender,
            "report_date": report_date.strftime("%d %B %Y"),
            "report_type": report_type,
            "clinical_notes": clinical_notes,
            "include_evidence": include_evidence,
        }

        if include_risk and has_risk:
            r = st.session_state["risk_result"]
            report_data["risk_result"] = {
                "kidney_health_score": r.kidney_health_score,
                "risk_score": r.risk_score,
                "risk_category": r.risk_category,
                "ckd_stage": r.ckd_stage,
                "ckd_stage_num": r.ckd_stage_num,
                "egfr_category": r.egfr_category,
                "contributing_factors": r.contributing_factors,
                "recommendations": r.recommendations,
                "clinical_summary": r.clinical_summary,
                "monitoring_priority": r.monitoring_priority,
            }

        if include_med and has_med:
            m = st.session_state["medication_result"]
            report_data["medication_result"] = {
                "overall_risk": m.overall_risk,
                "flags": [{"drug": f.drug, "flag_type": f.flag_type, "severity": f.severity,
                           "detail": f.detail, "action": f.action} for f in m.flags],
                "monitoring_requirements": m.monitoring_requirements,
                "ai_narrative": m.ai_narrative,
            }

        if include_econ and has_econ:
            e = st.session_state["economic_result"]
            report_data["economic_result"] = {
                "direct_medical_annual": e.direct_medical_annual,
                "direct_non_medical_annual": e.direct_non_medical_annual,
                "indirect_annual": e.indirect_annual,
                "total_annual": e.total_annual,
                "income_burden_pct": e.income_burden_pct,
                "financial_risk_category": e.financial_risk_category,
                "financial_burden_score": e.financial_burden_score,
                "ai_narrative": e.ai_narrative,
            }

        with st.spinner("Generating professional PDF report..."):
            pdf_bytes = generate_report(report_data)

        filename = f"RenalCare_Report_{patient_name.replace(' ', '_')}_{report_date.strftime('%Y%m%d')}.pdf"

        st.success("âœ… Report generated successfully!")
        st.markdown("<br>", unsafe_allow_html=True)

        # Download
        st.download_button(
            label="â¬‡ï¸ Download PDF Report",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True,
        )

        # Preview
        st.markdown("---")
        st.markdown("### ðŸ“„ Report Preview")
        _render_report_preview(report_data)

    else:
        st.markdown("<br>", unsafe_allow_html=True)
        if not (has_risk or has_med or has_econ):
            st.markdown("""
            <div class='info-box'>
                ðŸ’¡ <b>Get started:</b> Complete at least one of the assessment modules
                (Kidney Risk, Medication Review, or Pharmacoeconomics) to generate a report.
                Your results will automatically appear here.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='success-box'>
                âœ… Data from completed modules is ready. Configure report options above and click
                <b>Generate PDF Report</b> to create your clinical report.
            </div>
            """, unsafe_allow_html=True)

        # Sample report preview
        st.markdown("### ðŸ‘ï¸ Sample Report Structure")
        sections = [
            ("ðŸ“‹", "Patient Summary", "Demographics, report date, ID"),
            ("ðŸ«€", "Kidney Risk Analysis", "Risk score, CKD stage, contributing factors, recommendations"),
            ("ðŸ’Š", "Medication Intelligence Review", "Drug safety flags, monitoring requirements, pharmacist notes"),
            ("ðŸ’°", "Pharmacoeconomic Analysis", "Cost breakdown, burden score, economic summary"),
            ("ðŸ“", "Clinical Notes", "Physician/pharmacist observations"),
            ("âš•ï¸", "Clinical Disclaimer", "Legal and professional disclaimers"),
        ]
        for icon, title, desc in sections:
            st.markdown(f"""
            <div style='background:white; border-radius:8px; padding:0.8rem 1rem; margin:0.3rem 0;
                        box-shadow:0 1px 4px rgba(0,0,0,0.06); display:flex; gap:1rem; align-items:center;'>
                <span style='font-size:1.5rem;'>{icon}</span>
                <div>
                    <div style='font-weight:600; color:#1e3a5f; font-size:0.9rem;'>{title}</div>
                    <div style='font-size:0.8rem; color:#718096;'>{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def _render_report_preview(data: dict):
    """Render an in-app HTML preview of the report."""
    risk = data.get("risk_result", {})
    med = data.get("medication_result", {})
    econ = data.get("economic_result", {})

    html = f"""
    <div style='background:white; border-radius:12px; padding:2rem; box-shadow:0 2px 12px rgba(0,0,0,0.1);
                max-width:800px; margin:0 auto; font-family: Georgia, serif;'>

        <!-- Header -->
        <div style='background:linear-gradient(135deg, #1e3a5f, #2980b9); padding:1.5rem; border-radius:8px;
                    color:white; margin-bottom:1.5rem; display:flex; justify-content:space-between;'>
            <div>
                <div style='font-size:1.4rem; font-weight:700;'>ðŸ«€ RenalCare AI</div>
                <div style='font-size:0.85rem; color:#bde0fe;'>AI-Powered Kidney Disease Intelligence Report</div>
            </div>
            <div style='text-align:right; font-size:0.82rem; color:#bde0fe;'>
                Patient: <b style='color:white;'>{data.get("patient_name","â€”")}</b><br>
                Date: {data.get("report_date","â€”")}<br>
                Type: {data.get("report_type","Clinical Report")}
            </div>
        </div>

        <!-- Patient Summary -->
        <div style='background:#f8fafc; border-radius:8px; padding:1rem; margin-bottom:1rem;
                    border-left:4px solid #1e3a5f;'>
            <div style='font-weight:700; color:#1e3a5f; margin-bottom:0.5rem; font-size:0.9rem;'>PATIENT SUMMARY</div>
            <div style='font-size:0.85rem; color:#4a5568;'>
                Name: {data.get("patient_name","â€”")} &nbsp;|&nbsp;
                Age: {data.get("patient_age","â€”")} years &nbsp;|&nbsp;
                Gender: {data.get("patient_gender","â€”")}
            </div>
        </div>
    """

    if risk:
        cat = risk.get("risk_category", "â€”")
        cat_colors = {"Low": "#27ae60", "Moderate": "#e67e22", "High": "#e74c3c", "Critical": "#8e44ad"}
        cc = cat_colors.get(cat, "#718096")
        html += f"""
        <div style='background:#ebf5fb; border-radius:8px; padding:1rem; margin-bottom:1rem;
                    border-left:4px solid #2980b9;'>
            <div style='font-weight:700; color:#2980b9; margin-bottom:0.5rem; font-size:0.9rem;'>KIDNEY RISK ANALYSIS</div>
            <div style='display:flex; gap:2rem;'>
                <div>
                    <span style='font-size:0.8rem; color:#718096;'>Risk Score</span><br>
                    <span style='font-size:1.5rem; font-weight:700; color:#e74c3c;'>{risk.get("risk_score","â€”")}/100</span>
                </div>
                <div>
                    <span style='font-size:0.8rem; color:#718096;'>Classification</span><br>
                    <span style='font-size:1.1rem; font-weight:700; color:{cc};'>{cat}</span>
                </div>
                <div>
                    <span style='font-size:0.8rem; color:#718096;'>CKD Stage</span><br>
                    <span style='font-size:1.1rem; font-weight:700; color:#1e3a5f;'>{risk.get("ckd_stage","â€”")}</span>
                </div>
            </div>
            <div style='font-size:0.82rem; color:#4a5568; margin-top:0.5rem;'>{risk.get("clinical_summary","")}</div>
        </div>
        """

    if med:
        flags = med.get("flags", [])
        html += f"""
        <div style='background:#f3e8ff; border-radius:8px; padding:1rem; margin-bottom:1rem;
                    border-left:4px solid #8e44ad;'>
            <div style='font-weight:700; color:#8e44ad; margin-bottom:0.5rem; font-size:0.9rem;'>MEDICATION INTELLIGENCE REVIEW</div>
            <div style='font-size:0.85rem;'>Overall Risk: <b>{med.get("overall_risk","â€”")}</b> Â· {len(flags)} flag(s) identified</div>
        </div>
        """

    if econ:
        html += f"""
        <div style='background:#fdf2e9; border-radius:8px; padding:1rem; margin-bottom:1rem;
                    border-left:4px solid #e67e22;'>
            <div style='font-weight:700; color:#e67e22; margin-bottom:0.5rem; font-size:0.9rem;'>PHARMACOECONOMIC ANALYSIS</div>
            <div style='display:flex; gap:2rem;'>
                <div>
                    <span style='font-size:0.8rem; color:#718096;'>Annual Cost</span><br>
                    <span style='font-size:1.3rem; font-weight:700; color:#e74c3c;'>â‚¹{econ.get("total_annual",0):,.0f}</span>
                </div>
                <div>
                    <span style='font-size:0.8rem; color:#718096;'>Income Burden</span><br>
                    <span style='font-size:1.3rem; font-weight:700; color:#e67e22;'>{econ.get("income_burden_pct",0):.1f}%</span>
                </div>
                <div>
                    <span style='font-size:0.8rem; color:#718096;'>Financial Risk</span><br>
                    <span style='font-size:1.1rem; font-weight:700; color:#8e44ad;'>{econ.get("financial_risk_category","â€”")}</span>
                </div>
            </div>
        </div>
        """

    notes = data.get("clinical_notes", "")
    if notes:
        html += f"""
        <div style='background:#f8f9fa; border-radius:8px; padding:1rem; margin-bottom:1rem;'>
            <div style='font-weight:700; color:#4a5568; margin-bottom:0.5rem; font-size:0.9rem;'>CLINICAL NOTES</div>
            <div style='font-size:0.85rem; color:#4a5568;'>{notes}</div>
        </div>
        """

    html += """
        <div style='background:#f0f0f0; border-radius:6px; padding:0.8rem; font-size:0.75rem; color:#718096; font-style:italic;'>
            âš•ï¸ This report is generated by RenalCare AI AI Platform for clinical decision support only.
            It does not constitute medical advice and does not replace the clinical judgment of qualified healthcare professionals.
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
