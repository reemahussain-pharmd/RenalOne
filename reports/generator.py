"""
AI Renal Report Generator — RenalCare AI
Professional PDF report generation using ReportLab.
"""
import sys
import io
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# ---- Colour palette ----
NAVY   = colors.HexColor("#1e3a5f")
BLUE   = colors.HexColor("#2980b9")
TEAL   = colors.HexColor("#16a085")
GREEN  = colors.HexColor("#27ae60")
ORANGE = colors.HexColor("#e67e22")
RED    = colors.HexColor("#e74c3c")
GREY   = colors.HexColor("#7f8c8d")
LIGHT  = colors.HexColor("#ecf0f1")
WHITE  = colors.white


def _risk_color(category: str):
    return {"Low": GREEN, "Moderate": ORANGE, "High": RED, "Critical": RED, "Catastrophic": RED}.get(category, GREY)


def _styles():
    base = getSampleStyleSheet()
    custom = {
        "title": ParagraphStyle("title", fontSize=22, textColor=WHITE, alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=4),
        "subtitle": ParagraphStyle("subtitle", fontSize=11, textColor=LIGHT, alignment=TA_CENTER, fontName="Helvetica", spaceAfter=2),
        "section": ParagraphStyle("section", fontSize=13, textColor=NAVY, fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6),
        "subsection": ParagraphStyle("subsection", fontSize=11, textColor=BLUE, fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle("body", fontSize=9, textColor=colors.HexColor("#2c3e50"), fontName="Helvetica", spaceAfter=4, leading=14),
        "small": ParagraphStyle("small", fontSize=8, textColor=GREY, fontName="Helvetica", spaceAfter=2),
        "disclaimer": ParagraphStyle("disclaimer", fontSize=8, textColor=GREY, fontName="Helvetica-Oblique", spaceAfter=4, borderPad=4),
        "badge_low": ParagraphStyle("badge", fontSize=10, textColor=GREEN, fontName="Helvetica-Bold"),
        "badge_mod": ParagraphStyle("badge", fontSize=10, textColor=ORANGE, fontName="Helvetica-Bold"),
        "badge_high": ParagraphStyle("badge", fontSize=10, textColor=RED, fontName="Helvetica-Bold"),
    }
    return base, custom


def _header_table(patient_name: str, report_date: str, report_id: str) -> Table:
    data = [[
        Paragraph(f"<font color='white' size=18><b>RenalCare AI</b></font>", ParagraphStyle("h", alignment=TA_LEFT, fontName="Helvetica-Bold", fontSize=18)),
        Paragraph(f"<font color='#ecf0f1' size=9>Patient: <b>{patient_name}</b><br/>Date: {report_date}<br/>Report ID: {report_id}</font>",
                  ParagraphStyle("hr", alignment=TA_RIGHT, fontName="Helvetica", fontSize=9)),
    ]]
    t = Table(data, colWidths=[10*cm, 9*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, 0), 12),
        ("RIGHTPADDING", (-1, 0), (-1, 0), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
    ]))
    return t


def _section_header(title: str, color=NAVY) -> list:
    _, s = _styles()
    return [
        Spacer(1, 0.3*cm),
        Table([[Paragraph(f"<b>{title}</b>", ParagraphStyle("sh", fontSize=12, textColor=WHITE, fontName="Helvetica-Bold"))]],
              colWidths=[19*cm]),
        _styled_table_style(color),
        Spacer(1, 0.15*cm),
    ]


def _styled_table_style(color):
    """Dummy — used only as marker; header drawn in _section_header."""
    return Spacer(1, 0.01*cm)


def _kv_table(rows: list[tuple], col_w=(7*cm, 12*cm)) -> Table:
    """Two-column key-value table."""
    data = [[Paragraph(f"<b>{k}</b>", ParagraphStyle("k", fontSize=9, fontName="Helvetica-Bold", textColor=NAVY)),
             Paragraph(str(v), ParagraphStyle("v", fontSize=9, fontName="Helvetica"))]
            for k, v in rows]
    t = Table(data, colWidths=list(col_w))
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eaf4fb")),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#d0d7de")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def generate_report(report_data: dict) -> bytes:
    """
    Generate a professional PDF report.

    report_data keys:
        patient_name, patient_age, patient_gender, report_date,
        risk_result (dict), medication_result (dict),
        nutrition_items (list), economic_result (dict),
        clinical_notes (str), include_evidence (bool)
    """
    if not REPORTLAB_AVAILABLE:
        return _fallback_text_report(report_data)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=2*cm,
    )
    _, s = _styles()
    story = []

    patient_name = report_data.get("patient_name", "Anonymous Patient")
    report_date = report_data.get("report_date", datetime.now().strftime("%d %B %Y"))
    report_id = f"RC-{datetime.now().strftime('%Y%m%d%H%M')}"

    # ---- COVER HEADER ----
    story.append(_header_table(patient_name, report_date, report_id))
    story.append(Spacer(1, 0.2*cm))

    tagline_style = ParagraphStyle("tag", fontSize=9, textColor=GREY, alignment=TA_CENTER, fontName="Helvetica-Oblique")
    story.append(Paragraph("AI-Powered Kidney Disease Intelligence Report", tagline_style))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT))
    story.append(Spacer(1, 0.3*cm))

    # ---- PATIENT SUMMARY ----
    story.append(_build_section_bar("PATIENT SUMMARY", NAVY))
    patient_rows = [
        ("Patient Name", patient_name),
        ("Age", f"{report_data.get('patient_age', '—')} years"),
        ("Gender", report_data.get("patient_gender", "—")),
        ("Report Date", report_date),
        ("Report ID", report_id),
    ]
    story.append(_kv_table(patient_rows))
    story.append(Spacer(1, 0.3*cm))

    # ---- KIDNEY RISK ANALYSIS ----
    risk = report_data.get("risk_result", {})
    if risk:
        story.append(_build_section_bar("KIDNEY RISK ANALYSIS", BLUE))
        cat = risk.get("risk_category", "—")
        risk_rows = [
            ("Kidney Health Score", f"{risk.get('kidney_health_score', '—')} / 100"),
            ("Risk Score", f"{risk.get('risk_score', '—')} / 100"),
            ("Risk Classification", cat),
            ("CKD Stage", risk.get("ckd_stage", "—")),
            ("eGFR Category", risk.get("egfr_category", "—")),
            ("Monitoring Priority", risk.get("monitoring_priority", "—")),
        ]
        story.append(_kv_table(risk_rows))
        story.append(Spacer(1, 0.2*cm))

        if risk.get("clinical_summary"):
            story.append(Paragraph("<b>Clinical Summary</b>", s["subsection"]))
            story.append(Paragraph(risk["clinical_summary"], s["body"]))

        factors = risk.get("contributing_factors", [])
        if factors:
            story.append(Paragraph("<b>Contributing Risk Factors</b>", s["subsection"]))
            factor_data = [["Risk Factor", "Value", "Impact"]] + [
                [f.get("factor", ""), f.get("value", ""), f.get("impact", "")]
                for f in factors
            ]
            ft = Table(factor_data, colWidths=[7*cm, 6*cm, 5*cm])
            ft.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), BLUE),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.3, LIGHT),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#f8fafc")]),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(ft)

        recs = risk.get("recommendations", [])
        if recs:
            story.append(Spacer(1, 0.2*cm))
            story.append(Paragraph("<b>Clinical Recommendations</b>", s["subsection"]))
            for r in recs:
                story.append(Paragraph(f"• {r}", s["body"]))
        story.append(Spacer(1, 0.3*cm))

    # ---- MEDICATION REVIEW ----
    med = report_data.get("medication_result", {})
    if med:
        story.append(_build_section_bar("MEDICATION INTELLIGENCE REVIEW", TEAL))
        story.append(Paragraph(f"<b>Overall Medication Risk:</b> {med.get('overall_risk', '—')}", s["body"]))
        story.append(Spacer(1, 0.1*cm))

        flags = med.get("flags", [])
        if flags:
            story.append(Paragraph("<b>Drug Safety Flags</b>", s["subsection"]))
            flag_data = [["Drug / Combination", "Flag Type", "Severity", "Key Concern"]] + [
                [f.get("drug", ""), f.get("flag_type", ""), f.get("severity", ""), f.get("detail", "")[:60] + "…"]
                for f in flags
            ]
            ft = Table(flag_data, colWidths=[4.5*cm, 3.5*cm, 2.5*cm, 8.5*cm])
            ft.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), TEAL),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                ("GRID", (0, 0), (-1, -1), 0.3, LIGHT),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#f0faf8")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("WORDWRAP", (3, 0), (3, -1), True),
            ]))
            story.append(ft)

        monitoring = med.get("monitoring_requirements", [])
        if monitoring:
            story.append(Spacer(1, 0.15*cm))
            story.append(Paragraph("<b>Monitoring Requirements</b>", s["subsection"]))
            for m in monitoring:
                story.append(Paragraph(f"• {m}", s["body"]))

        if med.get("ai_narrative"):
            story.append(Spacer(1, 0.15*cm))
            story.append(Paragraph("<b>Clinical Pharmacist AI Review</b>", s["subsection"]))
            narrative = med["ai_narrative"].replace("**", "").replace("*", "")
            story.append(Paragraph(narrative, s["body"]))
        story.append(Spacer(1, 0.3*cm))

    # ---- ECONOMIC ANALYSIS ----
    econ = report_data.get("economic_result", {})
    if econ:
        story.append(_build_section_bar("PHARMACOECONOMIC ANALYSIS", colors.HexColor("#8e44ad")))
        econ_rows = [
            ("Direct Medical Cost (Annual)", f"₹{econ.get('direct_medical_annual', 0):,.0f}"),
            ("Direct Non-Medical Cost (Annual)", f"₹{econ.get('direct_non_medical_annual', 0):,.0f}"),
            ("Indirect Cost (Annual)", f"₹{econ.get('indirect_annual', 0):,.0f}"),
            ("Total Estimated Annual Cost", f"₹{econ.get('total_annual', 0):,.0f}"),
            ("Income Burden", f"{econ.get('income_burden_pct', 0):.1f}% of annual income"),
            ("Financial Risk Category", econ.get("financial_risk_category", "—")),
            ("Financial Burden Score", f"{econ.get('financial_burden_score', 0):.1f} / 100"),
        ]
        story.append(_kv_table(econ_rows))
        if econ.get("ai_narrative"):
            story.append(Spacer(1, 0.15*cm))
            story.append(Paragraph("<b>Economic Burden Assessment</b>", s["subsection"]))
            narrative = econ["ai_narrative"].replace("**", "").replace("*", "")
            story.append(Paragraph(narrative, s["body"]))
        story.append(Spacer(1, 0.3*cm))

    # ---- CLINICAL NOTES ----
    notes = report_data.get("clinical_notes", "")
    if notes:
        story.append(_build_section_bar("CLINICAL NOTES", GREY))
        story.append(Paragraph(notes, s["body"]))
        story.append(Spacer(1, 0.3*cm))

    # ---- DISCLAIMER ----
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT))
    story.append(Spacer(1, 0.2*cm))
    disclaimer = (
        "⚕️ CLINICAL DISCLAIMER: This report is generated by RenalCare AI AI Platform for clinical decision support only. "
        "It does not constitute medical advice and does not replace the clinical judgment of qualified physicians, "
        "pharmacists, or other licensed healthcare professionals. All clinical decisions must be made by authorised "
        "healthcare providers based on a complete assessment of the individual patient. "
        "RenalCare AI | Version 1.0 | Generated: " + report_date
    )
    story.append(Paragraph(disclaimer, s["disclaimer"]))

    doc.build(story)
    return buf.getvalue()


def _build_section_bar(title: str, color) -> Table:
    """Full-width coloured section header bar."""
    t = Table(
        [[Paragraph(f"<font color='white'><b>{title}</b></font>",
                    ParagraphStyle("sb", fontSize=11, fontName="Helvetica-Bold"))]],
        colWidths=[19*cm],
    )
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def _fallback_text_report(data: dict) -> bytes:
    """Plain text fallback when ReportLab is not installed."""
    lines = [
        "=" * 60,
        "RenalCare AI — AI RENAL INTELLIGENCE REPORT",
        "=" * 60,
        f"Patient: {data.get('patient_name', '—')}",
        f"Date: {data.get('report_date', datetime.now().strftime('%d %B %Y'))}",
        "",
    ]
    risk = data.get("risk_result", {})
    if risk:
        lines += [
            "KIDNEY RISK ANALYSIS",
            "-" * 30,
            f"Risk Category: {risk.get('risk_category', '—')}",
            f"Risk Score: {risk.get('risk_score', '—')}/100",
            f"CKD Stage: {risk.get('ckd_stage', '—')}",
            "",
        ]
    lines.append("Generated by RenalCare AI AI Platform.")
    return "\n".join(lines).encode("utf-8")
