"""Clinical Evidence Intelligence Page — RenalCare OS."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from rag.engine import get_rag_engine, BUILT_IN_KNOWLEDGE


EXAMPLE_QUESTIONS = [
    "What are the KDIGO blood pressure targets for CKD patients?",
    "What evidence supports SGLT2 inhibitors in CKD?",
    "Should metformin be used in patients with eGFR below 45?",
    "What dietary recommendations are advised for CKD Stage 3 patients?",
    "How should anaemia be managed in CKD?",
    "What are the risks of dual RAAS blockade in CKD?",
    "How does CKD affect bone mineral metabolism?",
    "What is the economic burden of hemodialysis in India?",
]


def render():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #0d5c4a, #16a085);
                border-radius: 12px; padding: 1.5rem 2rem; margin-bottom: 1.5rem;'>
        <h2 style='color:white; margin:0; font-size:1.5rem;'>🔬 Clinical Evidence Intelligence</h2>
        <p style='color:#a7f3d0; margin:0.3rem 0 0 0; font-size:0.88rem;'>
            RAG-powered nephrology knowledge base · KDIGO Guidelines · Research Evidence
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='info-box'>
        <b>⚕️ Disclaimer:</b> This system provides evidence-based insights and does not replace clinical judgment.
        All clinical decisions must be made by qualified healthcare professionals.
    </div>
    """, unsafe_allow_html=True)

    rag = get_rag_engine()

    # Layout
    left, right = st.columns([1.6, 1])

    with right:
        st.markdown("### 📚 Knowledge Base")
        st.markdown(f"""
        <div style='background:white; border-radius:10px; padding:1rem; box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
            <div style='display:flex; justify-content:space-between; margin-bottom:0.8rem;'>
                <span style='font-size:0.85rem; font-weight:600; color:#1e3a5f;'>Built-in KDIGO Articles</span>
                <span style='background:#d5f5e3; color:#1e8449; padding:2px 8px; border-radius:10px; font-size:0.75rem;'>
                    {len(BUILT_IN_KNOWLEDGE)} sources
                </span>
            </div>
        """, unsafe_allow_html=True)
        for item in BUILT_IN_KNOWLEDGE[:6]:
            st.markdown(f"""
            <div style='padding:0.4rem 0; border-bottom:1px solid #f0f0f0;'>
                <div style='font-size:0.8rem; font-weight:600; color:#2980b9;'>{item["title"]}</div>
                <div style='font-size:0.72rem; color:#718096;'>{item["source"]}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # PDF upload
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📄 Upload Research Papers")
        uploaded = st.file_uploader(
            "Upload PDF (clinical guidelines, research papers)",
            type=["pdf"],
            help="Upload PDF files to expand the knowledge base",
        )
        if uploaded:
            with st.spinner("Processing PDF..."):
                n = rag.add_pdf(uploaded.read(), uploaded.name)
            if n > 0:
                st.success(f"✅ Added {n} text segments from '{uploaded.name}'")
            else:
                st.warning("Could not extract text. Ensure PDF contains selectable text.")

        if rag.has_uploaded_documents():
            st.markdown("""
            <div style='background:#d5f5e3; border-radius:8px; padding:0.5rem 0.8rem; font-size:0.8rem; color:#1e8449;'>
                📂 Custom documents loaded into knowledge base
            </div>
            """, unsafe_allow_html=True)

        # Example questions
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 💡 Example Questions")
        for q in EXAMPLE_QUESTIONS[:5]:
            if st.button(q, key=f"eg_{q[:20]}", use_container_width=True):
                st.session_state["rag_query"] = q
                st.rerun()

    with left:
        st.markdown("### 🔍 Ask a Clinical Question")

        query = st.text_area(
            "Enter your clinical question",
            value=st.session_state.get("rag_query", ""),
            height=100,
            placeholder="e.g. What are the KDIGO recommendations for blood pressure targets in CKD patients with diabetes?",
        )

        if "rag_query" in st.session_state:
            del st.session_state["rag_query"]

        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)

        if search_clicked and query.strip():
            with st.spinner("Retrieving clinical evidence..."):
                result = rag.answer_query(query.strip())

            st.session_state["evidence_result"] = result
            st.markdown("---")
            st.markdown("### 📋 Evidence Summary")

            # Source cards
            sources = result.get("sources", [])
            if sources:
                st.markdown(f"<div style='font-size:0.8rem; color:#718096; margin-bottom:0.5rem;'>📚 Retrieved {len(sources)} relevant source(s) {'using semantic search' if result.get('vector_search_used') else 'using keyword matching'}</div>", unsafe_allow_html=True)
                for i, src in enumerate(sources, 1):
                    with st.expander(f"[{i}] {src.get('title', 'Source')} — {src.get('source', '')}"):
                        st.markdown(f"<div style='font-size:0.85rem; color:#4a5568; line-height:1.6;'>{src['text']}</div>", unsafe_allow_html=True)

            # AI answer
            st.markdown("<br>", unsafe_allow_html=True)
            ai_answer = result.get("answer", "")
            if ai_answer:
                st.markdown(f"""
                <div style='background:white; border-radius:10px; padding:1.5rem; box-shadow:0 2px 8px rgba(0,0,0,0.06);
                            border-left:4px solid #16a085; line-height:1.7;'>
                """, unsafe_allow_html=True)
                st.markdown(ai_answer)
                st.markdown("</div>", unsafe_allow_html=True)

        elif search_clicked and not query.strip():
            st.warning("Please enter a clinical question.")

        elif not search_clicked:
            # Welcome state
            st.markdown("""
            <div style='background:white; border-radius:12px; padding:2rem; text-align:center;
                        box-shadow:0 2px 8px rgba(0,0,0,0.06); margin-top:1rem;'>
                <div style='font-size:2.5rem; margin-bottom:0.8rem;'>🔬</div>
                <h4 style='color:#1e3a5f;'>Nephrology Evidence Engine</h4>
                <p style='color:#718096; font-size:0.88rem; line-height:1.6;'>
                    Ask any clinical question about CKD management, medications, nutrition,
                    or dialysis. The system retrieves evidence from the built-in KDIGO knowledge
                    base and any PDFs you upload.
                </p>
                <div style='display:flex; flex-wrap:wrap; gap:0.5rem; justify-content:center; margin-top:1rem;'>
                    <span style='background:#e8f4fd; color:#2980b9; padding:4px 12px; border-radius:12px; font-size:0.78rem;'>KDIGO 2024</span>
                    <span style='background:#e8f4fd; color:#2980b9; padding:4px 12px; border-radius:12px; font-size:0.78rem;'>SGLT2i Evidence</span>
                    <span style='background:#e8f4fd; color:#2980b9; padding:4px 12px; border-radius:12px; font-size:0.78rem;'>Drug Safety</span>
                    <span style='background:#e8f4fd; color:#2980b9; padding:4px 12px; border-radius:12px; font-size:0.78rem;'>Nutrition</span>
                    <span style='background:#e8f4fd; color:#2980b9; padding:4px 12px; border-radius:12px; font-size:0.78rem;'>Economic Burden</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Previous result
        if "evidence_result" in st.session_state and not search_clicked:
            prev = st.session_state["evidence_result"]
            st.markdown("---")
            st.markdown(f"<div style='font-size:0.8rem; color:#718096;'>Last query: <i>{prev['query']}</i></div>", unsafe_allow_html=True)
