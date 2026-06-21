"""Dashboard Home Page — RenalCare AI."""

import streamlit as st
from components.styles import sh
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


def go(page: str):
    st.session_state.current_page = page
    st.rerun()


def render():
    # ── Hero Banner ────────────────────────────────────────────────────────
    sh("""
    <div style="background:linear-gradient(135deg,#0F1F3D 0%,#1E3A5F 45%,#0F4C5C 100%);
                border-radius:20px;padding:2.5rem 3rem;margin-bottom:1.5rem;
                position:relative;overflow:hidden;">
        <div style="position:absolute;top:-40px;right:-40px;width:220px;height:220px;
                    background:rgba(20,184,166,0.1);border-radius:50%;"></div>
        <div style="position:absolute;bottom:-60px;right:80px;width:300px;height:300px;
                    background:rgba(99,102,241,0.07);border-radius:50%;"></div>
        <div style="position:relative;z-index:1;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem;">
                <div style="background:rgba(20,184,166,0.2);border:1px solid rgba(20,184,166,0.3);
                            border-radius:8px;padding:4px 12px;font-size:0.72rem;font-weight:700;
                            color:#2DD4BF;letter-spacing:0.06em;text-transform:uppercase;">
                    Clinical AI Platform
                </div>
                <div style="background:rgba(99,102,241,0.2);border:1px solid rgba(99,102,241,0.3);
                            border-radius:8px;padding:4px 12px;font-size:0.72rem;font-weight:700;
                            color:#A5B4FC;letter-spacing:0.06em;text-transform:uppercase;">
                    KDIGO Evidence-Based
                </div>
            </div>
            <h1 style="color:white;font-size:2.2rem;font-weight:900;margin:0 0 0.6rem 0;
                       letter-spacing:-0.03em;line-height:1.15;">
                RenalCare AI
            </h1>
            <p style="color:rgba(255,255,255,0.7);font-size:1rem;margin:0 0 1.5rem 0;
                      max-width:600px;line-height:1.6;">
                Enterprise-grade kidney disease intelligence platform built on published clinical
                research and KDIGO 2024 guidelines. Six integrated modules for comprehensive
                renal care decision support.
            </p>
            <div style="display:flex;gap:10px;flex-wrap:wrap;">
                <div style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);
                            border-radius:8px;padding:6px 14px;font-size:0.8rem;color:rgba(255,255,255,0.8);
                            font-weight:500;">
                    \U0001f3e5 Clinical Decision Support
                </div>
                <div style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);
                            border-radius:8px;padding:6px 14px;font-size:0.8rem;color:rgba(255,255,255,0.8);
                            font-weight:500;">
                    \U0001f4ca Pharmacoeconomic Analysis
                </div>
                <div style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);
                            border-radius:8px;padding:6px 14px;font-size:0.8rem;color:rgba(255,255,255,0.8);
                            font-weight:500;">
                    \U0001f916 GPT-4o AI Integration
                </div>
            </div>
        </div>
    </div>
    """)

    # ── KPI Stats Row ──────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        ("#14B8A6", "\U0001fac0", "6", "Clinical Modules"),
        ("#6366F1", "\U0001f50d", "13+", "KDIGO Evidence Articles"),
        ("#F59E0B", "\U0001f4ca", "15+", "Cost Metrics Tracked"),
        ("#10B981", "\U0001f48a", "200+", "Drug Interactions Checked"),
    ]
    for col, (color, icon, value, label) in zip([k1, k2, k3, k4], kpis):
        with col:
            sh(f"""
            <div class="kpi-card">
                <div class="kpi-icon" style="background:{color}18;">
                    <span style="font-size:1.3rem;">{icon}</span>
                </div>
                <div class="kpi-value" style="color:{color};">{value}</div>
                <div class="kpi-label">{label}</div>
            </div>
            """)

    sh("<div style='margin-top:1.5rem;'></div>")

    # ── Section header ─────────────────────────────────────────────────────
    sh("""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
        <div>
            <div style="font-size:1.1rem;font-weight:800;color:#0F172A;">Clinical Intelligence Modules</div>
            <div style="font-size:0.82rem;color:#64748B;margin-top:2px;">
                Six integrated modules covering the full renal care workflow
            </div>
        </div>
        <div style="background:#F1F5F9;border-radius:20px;padding:4px 12px;font-size:0.75rem;
                    font-weight:600;color:#64748B;">V1 — All Active</div>
    </div>
    """)

    # ── Module Cards ───────────────────────────────────────────────────────
    modules = [
        ("Risk",       "#EF4444", "#FEE2E2", "❤️",         "Kidney Risk Assessment",
         "Multi-variable CKD risk scoring using eGFR, albuminuria, comorbidities, and lifestyle factors."),
        ("Evidence",   "#3B82F6", "#EFF6FF", "\U0001f50d",  "Clinical Evidence Intelligence",
         "KDIGO-powered RAG system. Query 13+ clinical articles with GPT-4o semantic search."),
        ("Medication", "#6366F1", "#EEF2FF", "\U0001f48a",  "Medication Intelligence",
         "PharmD-grade nephrotoxicity screening, renal dose adjustment, and drug-drug interactions."),
        ("Nutrition",  "#10B981", "#D1FAE5", "\U0001f966",  "Kidney Nutrition Intelligence",
         "Analyze 37+ foods for potassium, phosphorus, sodium. AI-generated personalized meal guidance."),
        ("Economics",  "#F59E0B", "#FEF3C7", "\U0001f4ca",  "Pharmacoeconomic Intelligence",
         "Cost-of-illness modeling from published hemodialysis burden research in rural India."),
        ("Report",     "#14B8A6", "#CCFBF1", "\U0001f4c4",  "Clinical Report Generator",
         "Generate professional PDF reports aggregating risk, medication, and economic assessments."),
    ]

    r1_cols = st.columns(3)
    r2_cols = st.columns(3)

    for i, (key, color, bg, icon, title, desc) in enumerate(modules):
        col = r1_cols[i] if i < 3 else r2_cols[i - 3]
        with col:
            clicked = st.button(
                "▶  Open Module",
                key=f"mod_{key}",
                use_container_width=False,
            )
            sh(f"""
            <div class="module-card" style="border-top:3px solid {color};">
                <div class="module-icon" style="background:{bg};">
                    <span style="font-size:1.5rem;">{icon}</span>
                </div>
                <div class="module-title">{title}</div>
                <div class="module-desc">{desc}</div>
                <div style="display:inline-flex;align-items:center;gap:5px;
                            font-size:0.78rem;font-weight:600;color:{color};
                            background:{bg};padding:4px 10px;border-radius:20px;">
                    <span>Active</span>
                    <span style="font-size:0.7rem;">&#x2022;</span>
                    <span>AI-Powered</span>
                </div>
            </div>
            """)
            if clicked:
                go(key)

    sh("<div style='margin-top:1.8rem;'></div>")

    # ── Two-column info row ────────────────────────────────────────────────
    left, right = st.columns([1.2, 1])

    with left:
        sh("""
        <div class="rc-card">
            <div class="section-title">
                <span>\U0001f4da</span> Clinical Evidence Foundation
            </div>
            <div style="display:flex;flex-direction:column;gap:0.6rem;">
                <div style="display:flex;align-items:flex-start;gap:10px;">
                    <div style="width:8px;height:8px;border-radius:50%;background:#14B8A6;
                                margin-top:5px;flex-shrink:0;"></div>
                    <div style="font-size:0.84rem;color:#334155;line-height:1.5;">
                        <strong style="color:#0F172A;">KDIGO 2024 Guidelines</strong> — CKD risk stratification,
                        monitoring intervals, and progression milestones
                    </div>
                </div>
                <div style="display:flex;align-items:flex-start;gap:10px;">
                    <div style="width:8px;height:8px;border-radius:50%;background:#6366F1;
                                margin-top:5px;flex-shrink:0;"></div>
                    <div style="font-size:0.84rem;color:#334155;line-height:1.5;">
                        <strong style="color:#0F172A;">Published Research</strong> — Pharmacoeconomic models
                        adapted from peer-reviewed hemodialysis burden studies
                    </div>
                </div>
                <div style="display:flex;align-items:flex-start;gap:10px;">
                    <div style="width:8px;height:8px;border-radius:50%;background:#F59E0B;
                                margin-top:5px;flex-shrink:0;"></div>
                    <div style="font-size:0.84rem;color:#334155;line-height:1.5;">
                        <strong style="color:#0F172A;">WHO Cost Standards</strong> — Catastrophic expenditure
                        thresholds and out-of-pocket burden analysis
                    </div>
                </div>
                <div style="display:flex;align-items:flex-start;gap:10px;">
                    <div style="width:8px;height:8px;border-radius:50%;background:#EF4444;
                                margin-top:5px;flex-shrink:0;"></div>
                    <div style="font-size:0.84rem;color:#334155;line-height:1.5;">
                        <strong style="color:#0F172A;">PharmD Expertise</strong> — Nephrotoxicity and renal
                        dosing protocols from clinical pharmacy practice
                    </div>
                </div>
            </div>
        </div>
        """)

    with right:
        sh("""
        <div class="rc-card">
            <div class="section-title">
                <span>\U0001f6e0</span> Technology Stack
            </div>
            <div style="display:flex;flex-direction:column;gap:0.5rem;">
        """)

        tech = [
            ("#EFF6FF", "#3B82F6", "GPT-4o-mini / Gemini", "AI Intelligence Engine"),
            ("#F0FDF4", "#10B981", "FAISS Vector DB", "Semantic Search & RAG"),
            ("#FEF3C7", "#F59E0B", "KDIGO Guidelines", "Clinical Knowledge Base"),
            ("#EEF2FF", "#6366F1", "ReportLab PDF", "Professional Report Engine"),
            ("#F1F5F9", "#64748B", "Streamlit Cloud", "Deployment Platform"),
        ]
        badges_html = ""
        for bg, color, name, role in tech:
            badges_html += f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:7px 10px;background:{bg};border-radius:8px;">
                <span style="font-size:0.82rem;font-weight:600;color:#0F172A;">{name}</span>
                <span style="font-size:0.72rem;color:{color};font-weight:500;">{role}</span>
            </div>
            """
        sh(badges_html + "</div></div>")

    # ── Disclaimer ─────────────────────────────────────────────────────────
    sh("""
    <div style="margin-top:1.5rem;background:#FFF7ED;border:1px solid #FED7AA;border-radius:10px;
                padding:0.9rem 1.2rem;display:flex;gap:0.8rem;align-items:flex-start;">
        <span style="font-size:1.1rem;flex-shrink:0;">⚠️</span>
        <div style="font-size:0.8rem;color:#92400E;line-height:1.55;">
            <strong>Clinical Disclaimer:</strong> RenalCare AI is a decision-support tool intended for
            educational and research purposes. All outputs must be reviewed by qualified healthcare
            professionals. This platform does not constitute medical advice or replace clinical judgment.
        </div>
    </div>
    """)
