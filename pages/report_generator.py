"""AI Renal Report Generator Page — RenalCare AI."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from components.styles import sh
from datetime import datetime


def render():
    sh("""
    <div class="page-header">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;">
            <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.5rem;">
                    <span style="font-size:1.5rem;">\U0001f4c4</span>
                    <span style="background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.9);
                                 font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:20px;
                                 letter-spacing:0.06em;">PDF REPORT ENGINE</span>
                </div>
                <h1 style="color:white !important;font-size:1.7rem !important;font-weight:800 !important;
                           margin:0 0 0.3rem 0 !important;">Clinical Report Generator</h1>
                <p style="color:rgba(255,255,255,0.72) !important;font-size:0.88rem !important;margin:0 !important;">
                    Aggregate assessments into a professional PDF report for clinical records
                </p>
            </div>
        </div>
    </div>
    """)

    # ── Data availability check ────────────────────────────────────────────
    risk_data = st.session_state.get("risk_result")
    med_data  = st.session_state.get("med_result")
    econ_data = st.session_state.get("econ_result")

    has_any = any([risk_data, med_data, econ_data])

    left_col, right_col = st.columns([1.1, 1.5])

    with left_col:
        # ── Data status panel ──────────────────────────────────────────────
        sh("""
        <div class="rc-card">
            <div class="section-title"><span>\U0001f4cb</span> Available Assessment Data</div>
        """)

        modules_status = [
            ("Kidney Risk Assessment", risk_data, "Risk",       "\U0001f9e0"),
            ("Medication Intelligence", med_data,  "Medication", "\U0001f48a"),
            ("Pharmacoeconomics",      econ_data,  "Economics",  "\U0001f4ca"),
        ]

        for name, data, page_key, icon in modules_status:
            has = data is not None
            color = "#10B981" if has else "#CBD5E1"
            bg    = "#D1FAE5" if has else "#F8FAFC"
            label = "Data Available" if has else "Not Completed"
            sh(f"""
            <div style="background:{bg};border:1px solid {color}30;border-radius:8px;
                        padding:0.7rem 0.9rem;margin-bottom:0.5rem;
                        display:flex;align-items:center;justify-content:space-between;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:1rem;">{icon}</span>
                    <span style="font-size:0.84rem;font-weight:600;color:#0F172A;">{name}</span>
                </div>
                <span style="font-size:0.72rem;font-weight:700;color:{color};
                             background:white;padding:3px 9px;border-radius:20px;
                             border:1px solid {color}40;">
                    {'&#x2713; ' if has else ''}{label}
                </span>
            </div>
            """)

        if not has_any:
            sh("""
            <div class="alert alert-warning" style="margin-top:0.8rem;">
                ⚠️ Complete at least one module assessment to generate a report.
            </div>
            """)

        sh('</div>')

        # ── Report config ──────────────────────────────────────────────────
        sh("<div style='margin-top:0.8rem;'></div>")
        sh("""
        <div class="rc-card">
            <div class="section-title"><span>\U00002699</span> Report Configuration</div>
        """)
        sh('</div>')

        patient_name = st.text_input("Patient Name / ID", placeholder="e.g. Patient A or MRN-001")
        provider     = st.text_input("Ordering Clinician", value="Dr. Reema Hussain, PharmD")
        institution  = st.text_input("Institution", value="RenalCare AI Clinic")

        include_risk = st.checkbox("Include Risk Assessment",  value=bool(risk_data), disabled=not risk_data)
        include_med  = st.checkbox("Include Medication Review", value=bool(med_data), disabled=not med_data)
        include_econ = st.checkbox("Include Economic Analysis", value=bool(econ_data), disabled=not econ_data)

        gen_btn = st.button(
            "\U0001f4c4  Generate PDF Report",
            type="primary",
            use_container_width=True,
            disabled=not has_any,
        )

    with right_col:
        if gen_btn and has_any:
            _generate_report(
                patient_name, provider, institution,
                risk_data if include_risk else None,
                med_data  if include_med  else None,
                econ_data if include_econ else None,
            )
        elif has_any:
            _render_preview(risk_data, med_data, econ_data)
        else:
            _render_empty_state()


def _generate_report(patient_name, provider, institution, risk_data, med_data, econ_data):
    try:
        from reports.generator import generate_report
        report_data = {
            "patient_name": patient_name or "Anonymous",
            "provider": provider,
            "institution": institution,
            "date": datetime.now().strftime("%B %d, %Y"),
            "risk_result":       risk_data,
            "med_result":        med_data,
            "econ_result":       econ_data,
            "nutrition_result":  st.session_state.get("nutrition_result"),
        }
        pdf_bytes = generate_report(report_data)

        fname = f"RenalCareAI_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        st.download_button(
            label="\U0001f4e5  Download Clinical Report (PDF)",
            data=pdf_bytes,
            file_name=fname,
            mime="application/pdf",
            use_container_width=True,
        )

        sh("""
        <div class="alert alert-success" style="margin-top:0.8rem;">
            ✅ <strong>Report generated successfully.</strong> Click the button above to download your
            professional PDF clinical report.
        </div>
        """)

        _render_preview(risk_data, med_data, econ_data, show_header=False)

    except Exception as e:
        st.error(f"Report generation error: {e}")
        st.info("Ensure ReportLab is installed: pip install reportlab")


def _render_preview(risk_data, med_data, econ_data, show_header=True):
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    if show_header:
        sh("""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.8rem;">
            <span style="background:#EFF6FF;color:#1D4ED8;font-size:0.75rem;font-weight:700;
                         padding:4px 12px;border-radius:20px;">Live Preview</span>
        </div>
        """)

    # Preview card
    preview_html = f"""
    <div style="background:white;border:1px solid #E2E8F0;border-radius:16px;
                padding:2rem;box-shadow:0 4px 24px rgba(0,0,0,0.06);">
        <div style="background:linear-gradient(135deg,#1E3A5F,#2563EB);border-radius:10px;
                    padding:1.5rem;margin-bottom:1.5rem;">
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <div>
                    <div style="font-size:1.2rem;font-weight:800;color:white;margin-bottom:3px;">
                        RenalCare AI — Clinical Intelligence Report
                    </div>
                    <div style="font-size:0.78rem;color:rgba(255,255,255,0.7);">
                        Generated: {now}
                    </div>
                </div>
                <div style="font-size:2rem;">\U0001fac0</div>
            </div>
        </div>
    """

    if risk_data:
        r = risk_data
        preview_html += f"""
        <div style="margin-bottom:1.2rem;">
            <div style="font-size:0.9rem;font-weight:800;color:#1E3A5F;border-bottom:2px solid #E2E8F0;
                        padding-bottom:6px;margin-bottom:0.8rem;">
                ❤️ Kidney Risk Assessment
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.6rem;">
                <div style="background:#FEE2E2;border-radius:8px;padding:0.6rem;text-align:center;">
                    <div style="font-size:1.3rem;font-weight:800;color:#991B1B;">{getattr(r, 'risk_score', 'N/A'):.0f}</div>
                    <div style="font-size:0.68rem;font-weight:600;color:#991B1B;text-transform:uppercase;">Risk Score</div>
                </div>
                <div style="background:#F1F5F9;border-radius:8px;padding:0.6rem;text-align:center;">
                    <div style="font-size:1rem;font-weight:800;color:#1E3A5F;">{getattr(r, 'ckd_stage', 'N/A')}</div>
                    <div style="font-size:0.68rem;font-weight:600;color:#64748B;text-transform:uppercase;">CKD Stage</div>
                </div>
                <div style="background:#F1F5F9;border-radius:8px;padding:0.6rem;text-align:center;">
                    <div style="font-size:1rem;font-weight:800;color:#1E3A5F;">{getattr(r, 'risk_level', 'N/A')}</div>
                    <div style="font-size:0.68rem;font-weight:600;color:#64748B;text-transform:uppercase;">Risk Level</div>
                </div>
            </div>
        </div>
        """

    if med_data:
        high_ct = len([f for f in getattr(med_data, 'flags', []) if getattr(f, 'severity', '') == 'HIGH'])
        total_ct = len(getattr(med_data, 'flags', []))
        preview_html += f"""
        <div style="margin-bottom:1.2rem;">
            <div style="font-size:0.9rem;font-weight:800;color:#1E3A5F;border-bottom:2px solid #E2E8F0;
                        padding-bottom:6px;margin-bottom:0.8rem;">
                \U0001f48a Medication Intelligence
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;">
                <div style="background:#FEE2E2;border-radius:8px;padding:0.6rem;text-align:center;">
                    <div style="font-size:1.3rem;font-weight:800;color:#991B1B;">{high_ct}</div>
                    <div style="font-size:0.68rem;font-weight:600;color:#991B1B;text-transform:uppercase;">Critical Alerts</div>
                </div>
                <div style="background:#FEF3C7;border-radius:8px;padding:0.6rem;text-align:center;">
                    <div style="font-size:1.3rem;font-weight:800;color:#92400E;">{total_ct}</div>
                    <div style="font-size:0.68rem;font-weight:600;color:#92400E;text-transform:uppercase;">Total Flags</div>
                </div>
            </div>
        </div>
        """

    if econ_data:
        preview_html += f"""
        <div style="margin-bottom:1.2rem;">
            <div style="font-size:0.9rem;font-weight:800;color:#1E3A5F;border-bottom:2px solid #E2E8F0;
                        padding-bottom:6px;margin-bottom:0.8rem;">
                \U0001f4ca Pharmacoeconomic Analysis
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;">
                <div style="background:#EFF6FF;border-radius:8px;padding:0.6rem;text-align:center;">
                    <div style="font-size:1.1rem;font-weight:800;color:#1D4ED8;">
                        ${getattr(econ_data, 'total_monthly_cost', 0):,.0f}
                    </div>
                    <div style="font-size:0.68rem;font-weight:600;color:#1D4ED8;text-transform:uppercase;">Monthly Cost</div>
                </div>
                <div style="background:{'#FEE2E2' if getattr(econ_data,'catastrophic_expenditure',False) else '#D1FAE5'};
                            border-radius:8px;padding:0.6rem;text-align:center;">
                    <div style="font-size:1.1rem;font-weight:800;
                                color:{'#991B1B' if getattr(econ_data,'catastrophic_expenditure',False) else '#065F46'};">
                        {'Catastrophic' if getattr(econ_data,'catastrophic_expenditure',False) else 'Manageable'}
                    </div>
                    <div style="font-size:0.68rem;font-weight:600;
                                color:{'#991B1B' if getattr(econ_data,'catastrophic_expenditure',False) else '#065F46'};
                                text-transform:uppercase;">WHO Threshold</div>
                </div>
            </div>
        </div>
        """

    preview_html += """
        <div style="background:#F8FAFC;border-radius:8px;padding:0.8rem;
                    font-size:0.75rem;color:#94A3B8;text-align:center;line-height:1.5;">
            This report is generated by RenalCare AI for educational and decision-support purposes only.
            All clinical decisions require review by a qualified healthcare professional.
        </div>
    </div>
    """
    sh(preview_html)


def _render_empty_state():
    sh("""
    <div style="background:white;border:2px dashed #E2E8F0;border-radius:16px;
                padding:3rem;text-align:center;">
        <div style="font-size:3rem;margin-bottom:1rem;">\U0001f4c4</div>
        <div style="font-size:1rem;font-weight:700;color:#0F172A;margin-bottom:0.5rem;">
            No Assessment Data Available
        </div>
        <div style="font-size:0.84rem;color:#64748B;max-width:380px;margin:0 auto;line-height:1.6;">
            Complete the Kidney Risk Assessment, Medication Review, or Pharmacoeconomic Analysis
            to generate a professional clinical report.
        </div>
        <div style="margin-top:1.5rem;display:flex;gap:8px;justify-content:center;flex-wrap:wrap;">
            <span style="background:#FEE2E2;color:#991B1B;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">
                ❤️ Risk Assessment
            </span>
            <span style="background:#EEF2FF;color:#3730A3;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">
                \U0001f48a Medication Review
            </span>
            <span style="background:#EFF6FF;color:#1E40AF;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">
                \U0001f4ca Economic Analysis
            </span>
        </div>
    </div>
    """)
