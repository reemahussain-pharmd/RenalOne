"""Clinical Evidence Intelligence Page — RenalOne."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from components.styles import sh
from rag.engine import get_rag_engine


EXAMPLE_QUERIES = [
    "What are the KDIGO CKD staging criteria?",
    "How often should eGFR be monitored in CKD G3b?",
    "What blood pressure targets are recommended for CKD patients?",
    "When should ACE inhibitors be used in diabetic nephropathy?",
    "What are the dietary protein recommendations for non-dialysis CKD?",
    "How does albuminuria affect CKD prognosis?",
]


def render():
    sh("""
    <div class="page-header">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;">
            <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.5rem;">
                    <span style="font-size:1.5rem;">\U0001f50d</span>
                    <span style="background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.9);
                                 font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:20px;
                                 letter-spacing:0.06em;">RAG-POWERED SEARCH</span>
                </div>
                <h1 style="color:white !important;font-size:1.7rem !important;font-weight:800 !important;
                           margin:0 0 0.3rem 0 !important;">Clinical Evidence Intelligence</h1>
                <p style="color:rgba(255,255,255,0.72) !important;font-size:0.88rem !important;margin:0 !important;">
                    KDIGO 2024 guidelines &bull; FAISS semantic search &bull; GPT-4o synthesis
                </p>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.7rem;color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:0.07em;">Knowledge Base</div>
                <div style="font-size:0.85rem;color:rgba(255,255,255,0.85);font-weight:600;">13 KDIGO Articles</div>
                <div style="font-size:0.85rem;color:rgba(255,255,255,0.85);font-weight:600;">FAISS + GPT-4o</div>
            </div>
        </div>
    </div>
    """)

    left_col, right_col = st.columns([1.5, 1])

    with left_col:
        # ── Query Input ────────────────────────────────────────────────────
        sh("""
        <div class="rc-card" style="margin-bottom:1rem;">
            <div class="section-title"><span>\U0001f4ac</span> Clinical Query</div>
        """)
        sh('</div>')

        query = st.text_area(
            "Ask a clinical question:",
            placeholder="e.g. 'What are KDIGO recommendations for CKD blood pressure targets?'",
            height=100,
            label_visibility="collapsed",
        )

        run_col, clear_col = st.columns([2, 1])
        with run_col:
            search_clicked = st.button("\U0001f50d  Search Clinical Evidence", type="primary", use_container_width=True)
        with clear_col:
            if st.button("Clear", use_container_width=True):
                st.session_state.pop("rag_result", None)
                st.rerun()

        # ── Results ────────────────────────────────────────────────────────
        if search_clicked and query.strip():
            with st.spinner("Searching KDIGO knowledge base..."):
                engine = get_rag_engine()
                result = engine.answer_query(query)
                st.session_state.rag_result = result

        if st.session_state.get("rag_result"):
            result = st.session_state.rag_result
            _render_answer(result)

        elif not search_clicked:
            sh("""
            <div style="background:#F8FAFC;border:2px dashed #E2E8F0;border-radius:12px;
                        padding:2.5rem;text-align:center;margin-top:0.5rem;">
                <div style="font-size:2.5rem;margin-bottom:0.8rem;">\U0001f50d</div>
                <div style="font-size:0.9rem;font-weight:600;color:#0F172A;margin-bottom:0.4rem;">
                    Query the Clinical Knowledge Base
                </div>
                <div style="font-size:0.83rem;color:#64748B;max-width:380px;margin:0 auto;line-height:1.6;">
                    Ask any question about CKD management, KDIGO guidelines, monitoring protocols,
                    or treatment recommendations.
                </div>
            </div>
            """)

    with right_col:
        # ── Knowledge base cards ───────────────────────────────────────────
        sh("""
        <div class="rc-card">
            <div class="section-title"><span>\U0001f4da</span> Knowledge Base</div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.8rem;">
                <span style="background:#D1FAE5;color:#065F46;font-size:0.72rem;font-weight:700;
                             padding:3px 10px;border-radius:20px;">13 KDIGO Articles</span>
                <span style="background:#EFF6FF;color:#1D4ED8;font-size:0.72rem;font-weight:700;
                             padding:3px 10px;border-radius:20px;">Always Available</span>
            </div>
        """)

        topics = [
            "\U0001f3e5 CKD Definition & Classification",
            "\U0001f4ca Risk Stratification Heat Map",
            "\U0001f9ea eGFR Monitoring Frequency",
            "\U0001f48a Blood Pressure Management",
            "\U0001f52c Albuminuria & Proteinuria",
            "\U0001f966 Dietary Interventions",
            "\U0001f489 Diabetes & CKD",
            "\U0001f4c8 CKD Progression Markers",
            "\U0001f9b8 Anemia in CKD",
            "\U0001f9b4 Mineral Bone Disorder",
            "\U0001f4dd Referral Guidelines",
            "\U0001fa78 Dialysis Initiation",
            "\U0001f4b0 Pharmacoeconomic Burden",
        ]
        for t in topics:
            sh(f'<div style="font-size:0.81rem;color:#374151;padding:4px 0;border-bottom:1px solid #F1F5F9;">{t}</div>')
        sh('</div>')

        sh("<div style='margin-top:0.8rem;'></div>")

        # ── Example questions ──────────────────────────────────────────────
        sh("""
        <div class="rc-card">
            <div class="section-title"><span>\U0001f4a1</span> Example Queries</div>
        """)
        sh('</div>')

        for i, q in enumerate(EXAMPLE_QUERIES):
            if st.button(q, key=f"ex_{i}", use_container_width=True):
                with st.spinner("Searching..."):
                    engine = get_rag_engine()
                    result = engine.answer_query(q)
                    st.session_state.rag_result = result
                    st.rerun()


def _render_answer(result):
    if isinstance(result, dict):
        answer   = result.get("answer", "")
        sources  = result.get("sources", [])
        n_sources = len(sources)
    else:
        answer   = str(result)
        sources  = []
        n_sources = 0

    sh(f"""
    <div style="margin-top:0.8rem;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.8rem;">
            <span style="background:#D1FAE5;color:#065F46;font-size:0.72rem;font-weight:700;
                         padding:3px 10px;border-radius:20px;">&#x2713; Answer Ready</span>
            <span style="background:#EFF6FF;color:#1D4ED8;font-size:0.72rem;font-weight:700;
                         padding:3px 10px;border-radius:20px;">{n_sources} sources cited</span>
        </div>
        <div style="background:linear-gradient(135deg,#EEF2FF 0%,#F0FDF4 100%);border-radius:12px;
                    padding:1.3rem;border:1px solid #C7D2FE;margin-bottom:0.8rem;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.7rem;">
                <span style="font-size:1rem;">\U0001f916</span>
                <span style="font-size:0.85rem;font-weight:700;color:#3730A3;">AI Clinical Response</span>
                <span style="background:#EEF2FF;color:#6366F1;font-size:0.65rem;font-weight:700;
                             padding:2px 8px;border-radius:20px;letter-spacing:0.05em;">GPT-4o</span>
            </div>
            <div style="font-size:0.87rem;color:#1E293B;line-height:1.72;">
                {answer.replace(chr(10), '<br>')}
            </div>
        </div>
    </div>
    """)

    if sources:
        sh('<div class="section-title"><span>\U0001f4da</span> Source Articles</div>')
        for src in sources[:4]:
            title   = src.get("title", "KDIGO Clinical Article") if isinstance(src, dict) else str(src)
            snippet = src.get("snippet", "")          if isinstance(src, dict) else ""
            sh(f"""
            <div style="background:white;border:1px solid #E2E8F0;border-radius:8px;
                        padding:0.8rem 1rem;margin-bottom:0.4rem;border-left:3px solid #3B82F6;">
                <div style="font-size:0.83rem;font-weight:700;color:#0F172A;margin-bottom:0.3rem;">
                    \U0001f4c4 {title}
                </div>
                {f'<div style="font-size:0.79rem;color:#64748B;line-height:1.5;">{snippet[:200]}...</div>' if snippet else ''}
            </div>
            """)
