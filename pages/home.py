"""Dashboard Home Page â€” RenalCare AI."""
import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


def render():
    # Hero section
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1e3a5f 0%, #2980b9 60%, #16a085 100%);
                border-radius: 16px; padding: 2.5rem 2rem; margin-bottom: 1.5rem; text-align: center;'>
        <div style='font-size: 3rem; margin-bottom: 0.5rem;'>ðŸ«€</div>
        <h1 style='color: white; font-size: 2.2rem; font-weight: 700; margin: 0; letter-spacing: -0.02em;'>
            RenalCare AI
        </h1>
        <p style='color: #bde0fe; font-size: 1.05rem; margin: 0.5rem 0 1rem 0;'>
            AI-Powered Kidney Disease Intelligence Platform
        </p>
        <div style='display: flex; gap: 0.5rem; justify-content: center; flex-wrap: wrap;'>
            <span style='background: rgba(255,255,255,0.15); color: white; padding: 4px 14px;
                         border-radius: 20px; font-size: 0.8rem; font-weight: 500;'>
                ðŸ§¬ Clinical Pharmacy AI
            </span>
            <span style='background: rgba(255,255,255,0.15); color: white; padding: 4px 14px;
                         border-radius: 20px; font-size: 0.8rem; font-weight: 500;'>
                ðŸ”¬ Evidence Intelligence
            </span>
            <span style='background: rgba(255,255,255,0.15); color: white; padding: 4px 14px;
                         border-radius: 20px; font-size: 0.8rem; font-weight: 500;'>
                ðŸ’Š Medication Safety
            </span>
            <span style='background: rgba(255,255,255,0.15); color: white; padding: 4px 14px;
                         border-radius: 20px; font-size: 0.8rem; font-weight: 500;'>
                ðŸ¥— Renal Nutrition
            </span>
            <span style='background: rgba(255,255,255,0.15); color: white; padding: 4px 14px;
                         border-radius: 20px; font-size: 0.8rem; font-weight: 500;'>
                ðŸ’° Pharmacoeconomics
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mission statement
    st.markdown("""
    <div class='info-box'>
        <b>ðŸŽ¯ Mission:</b> Transform kidney disease management from reactive treatment to predictive,
        preventive, and personalised care through AI â€” supporting clinicians, pharmacists, and researchers,
        not replacing them.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Platform modules
    st.markdown("### ðŸ¥ Platform Modules â€” Version 1")
    st.markdown("<br>", unsafe_allow_html=True)

    modules = [
        {
            "icon": "ðŸ«€",
            "title": "Kidney Risk Assessment",
            "desc": "AI-powered CKD risk scoring using clinical biomarkers, demographics, and comorbidities. Generates a 0â€“100 Kidney Health Score with risk classification.",
            "tags": ["Risk Score", "eGFR Analysis", "KDIGO Guidelines"],
            "color": "#2980b9",
            "page": "Risk",
            "status": "active",
        },
        {
            "icon": "ðŸ”¬",
            "title": "Clinical Evidence Intelligence",
            "desc": "RAG-powered clinical Q&A engine with built-in KDIGO guidelines knowledge base. Upload research papers for instant evidence retrieval.",
            "tags": ["RAG", "KDIGO", "PubMed"],
            "color": "#16a085",
            "page": "Evidence",
            "status": "active",
        },
        {
            "icon": "ðŸ’Š",
            "title": "Medication Intelligence",
            "desc": "Signature PharmD AI module. Drug interaction screening, nephrotoxicity alerts, renal dose adjustment review, and ADR risk assessment.",
            "tags": ["Drug Safety", "PharmD", "Nephrotoxicity"],
            "color": "#8e44ad",
            "page": "Medication",
            "status": "active",
        },
        {
            "icon": "ðŸ¥—",
            "title": "Kidney Nutrition Intelligence",
            "desc": "Personalised renal nutrition assistant. Analyse food suitability based on CKD stage with potassium, sodium, phosphorus, and protein guidance.",
            "tags": ["Renal Diet", "Nutrient Analysis", "CKD Stage"],
            "color": "#27ae60",
            "page": "Nutrition",
            "status": "active",
        },
        {
            "icon": "ðŸ’°",
            "title": "Pharmacoeconomic Intelligence",
            "desc": "Economic burden calculator based on published hemodialysis research. Estimates direct, indirect, and total annual costs with catastrophic expenditure analysis.",
            "tags": ["Cost Analysis", "Caregiver Burden", "Financial Risk"],
            "color": "#e67e22",
            "page": "Economics",
            "status": "active",
        },
        {
            "icon": "ðŸ“‹",
            "title": "AI Renal Report Generator",
            "desc": "Generate comprehensive, professional PDF clinical reports combining risk analysis, medication review, nutrition assessment, and economic burden data.",
            "tags": ["PDF Export", "Clinical Report", "Patient Summary"],
            "color": "#c0392b",
            "page": "Report",
            "status": "active",
        },
    ]

    cols = st.columns(3)
    for i, mod in enumerate(modules):
        with cols[i % 3]:
            st.markdown(f"""
            <div style='background: white; border-radius: 12px; padding: 1.3rem;
                        box-shadow: 0 2px 12px rgba(0,0,0,0.07); margin-bottom: 1rem;
                        border-top: 4px solid {mod["color"]}; min-height: 220px;'>
                <div style='font-size: 1.8rem; margin-bottom: 0.5rem;'>{mod["icon"]}</div>
                <div style='font-size: 1rem; font-weight: 700; color: #1e3a5f; margin-bottom: 0.4rem;'>
                    {mod["title"]}
                </div>
                <div style='font-size: 0.82rem; color: #4a5568; line-height: 1.5; margin-bottom: 0.8rem;'>
                    {mod["desc"]}
                </div>
                <div style='display: flex; flex-wrap: wrap; gap: 4px;'>
                    {''.join(f'<span style="background:{mod["color"]}22; color:{mod["color"]}; font-size:0.7rem; padding:2px 8px; border-radius:12px; font-weight:500;">{t}</span>' for t in mod["tags"])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Open {mod['title'].split()[0]} â†’", key=f"open_{mod['page']}", use_container_width=True):
                st.session_state.current_page = mod["page"]
                st.rerun()

    st.markdown("---")

    # Future roadmap
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### ðŸ—ºï¸ Version Roadmap")
        st.markdown("""
        <div style='background: white; border-radius: 10px; padding: 1.2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06);'>
            <div style='margin-bottom: 0.8rem;'>
                <span style='background:#d5f5e3; color:#1e8449; padding:3px 10px; border-radius:12px; font-size:0.75rem; font-weight:700;'>
                    âœ… VERSION 1 â€” LIVE
                </span>
                <div style='font-size:0.82rem; color:#4a5568; margin-top:0.4rem; line-height:1.8;'>
                    Kidney Risk Â· Clinical Evidence Â· Medication Intelligence<br>
                    Nutrition Intelligence Â· Pharmacoeconomics Â· Report Generator
                </div>
            </div>
            <hr style='border-color:#f0f0f0;'>
            <div style='margin-bottom: 0.8rem;'>
                <span style='background:#fef9e7; color:#d35400; padding:3px 10px; border-radius:12px; font-size:0.75rem; font-weight:700;'>
                    ðŸ”® VERSION 2 â€” PLANNED
                </span>
                <div style='font-size:0.82rem; color:#4a5568; margin-top:0.4rem; line-height:1.8;'>
                    CKD Progression Prediction Â· Adherence Intelligence<br>
                    Dialysis Intelligence Â· Research-Grade Models
                </div>
            </div>
            <hr style='border-color:#f0f0f0;'>
            <div>
                <span style='background:#f3e8ff; color:#6b21a8; padding:3px 10px; border-radius:12px; font-size:0.75rem; font-weight:700;'>
                    ðŸš€ VERSION 3 â€” FUTURE
                </span>
                <div style='font-size:0.82rem; color:#4a5568; margin-top:0.4rem; line-height:1.8;'>
                    Kidney Digital Twin Â· Population Health Intelligence<br>
                    Hospital Integration Â· FHIR/EHR Connectivity
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### âš•ï¸ Clinical Philosophy")
        st.markdown("""
        <div style='background: white; border-radius: 10px; padding: 1.2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06);'>
            <div style='font-size: 0.88rem; color: #4a5568; line-height: 1.8;'>
                <b style='color:#1e3a5f;'>RenalCare AI acts as:</b><br><br>
                ðŸ§ª <b>AI Clinical Pharmacist</b> â€” Drug safety, dose optimization, monitoring<br><br>
                ðŸ¥ <b>AI Nephrology Assistant</b> â€” Risk stratification, evidence retrieval<br><br>
                ðŸ’° <b>AI Healthcare Economist</b> â€” Burden quantification, cost drivers<br><br>
                ðŸ¥— <b>AI Renal Dietitian</b> â€” Personalised nutrition guidance<br><br>
                <div style='background:#ebf8ff; border-left:3px solid #3182ce; padding:0.6rem 0.8rem; border-radius:4px; margin-top:0.5rem;'>
                    <b>Not replacing clinicians.</b><br>Augmenting clinical decision-making with evidence-based AI intelligence.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tech stack
    st.markdown("### ðŸ› ï¸ Technology Stack")
    tech_cols = st.columns(5)
    tech_items = [
        ("ðŸ", "Python", "Core Language"),
        ("âš¡", "Streamlit", "Frontend UI"),
        ("ðŸ¤–", "OpenAI / Gemini", "AI Engine"),
        ("ðŸ“Š", "Plotly", "Visualisation"),
        ("ðŸ—„ï¸", "FAISS", "Vector Search"),
    ]
    for col, (icon, name, desc) in zip(tech_cols, tech_items):
        with col:
            st.markdown(f"""
            <div style='background:white; border-radius:8px; padding:0.8rem; text-align:center;
                        box-shadow:0 1px 6px rgba(0,0,0,0.06);'>
                <div style='font-size:1.5rem;'>{icon}</div>
                <div style='font-size:0.8rem; font-weight:700; color:#1e3a5f;'>{name}</div>
                <div style='font-size:0.72rem; color:#718096;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center; font-size:0.75rem; color:#a0aec0;'>
        RenalCare AI v1.0 â€” Clinical Decision Support Only â€” Not a substitute for professional medical advice<br>
        Built on KDIGO Guidelines Â· Evidence-Based Clinical Pharmacy Â· Published Pharmacoeconomic Research
    </div>
    """, unsafe_allow_html=True)
