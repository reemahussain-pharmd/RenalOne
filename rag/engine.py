"""
Clinical Evidence Intelligence (RAG) â€” RenalCare AI
Retrieval-Augmented Generation for nephrology literature.
Falls back gracefully when optional deps (FAISS, sentence-transformers) are unavailable.
"""
import sys
import os
from pathlib import Path
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.helpers import get_ai_response

# ---- Optional heavy imports ----
try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    try:
        from pypdf import PdfReader
        PDF_AVAILABLE = True
    except ImportError:
        PDF_AVAILABLE = False

# ---- Built-in KDIGO / Nephrology knowledge base ----
BUILT_IN_KNOWLEDGE = [
    {
        "id": "kdigo_2024_ckd_def",
        "title": "KDIGO 2024 CKD Definition",
        "source": "KDIGO Clinical Practice Guidelines",
        "text": "Chronic Kidney Disease (CKD) is defined as abnormalities of kidney structure or function, present for more than 3 months. CKD is classified based on cause, GFR category (G1-G5), and albuminuria category (A1-A3). eGFR <60 mL/min/1.73mÂ² or markers of kidney damage for >3 months confirms CKD regardless of cause.",
    },
    {
        "id": "kdigo_bp_target",
        "title": "Blood Pressure Targets in CKD",
        "source": "KDIGO 2021 Blood Pressure Guideline",
        "text": "KDIGO 2021 recommends a target systolic BP of <120 mmHg (standardised office measurement) for CKD patients. RAAS inhibitors (ACEi or ARB) are recommended for CKD patients with diabetes and albuminuria â‰¥30 mg/g, or for CKD patients without diabetes with albuminuria â‰¥300 mg/g.",
    },
    {
        "id": "sglt2_ckd",
        "title": "SGLT2 Inhibitors in CKD",
        "source": "CREDENCE, DAPA-CKD, EMPA-KIDNEY Trials",
        "text": "SGLT2 inhibitors (empagliflozin, dapagliflozin, canagliflozin) have demonstrated significant cardiorenal protection in CKD. DAPA-CKD trial showed 39% reduction in composite of â‰¥50% eGFR decline or ESRD or death from kidney/CV causes with dapagliflozin. KDIGO 2022 recommends SGLT2i for CKD patients with T2DM and eGFR â‰¥20.",
    },
    {
        "id": "raas_inhibition",
        "title": "RAAS Inhibition in CKD",
        "source": "KDIGO CKD Guidelines 2024",
        "text": "ACE inhibitors and ARBs reduce proteinuria and slow CKD progression. They are first-line in diabetic nephropathy with albuminuria. Dual RAAS blockade (ACEi + ARB) is not recommended due to increased risk of hyperkalaemia, hypotension, and acute kidney injury without additional benefit (ONTARGET trial). Monitor potassium and creatinine 1-2 weeks after initiation.",
    },
    {
        "id": "nutrition_ckd",
        "title": "Nutrition in CKD",
        "source": "KDIGO 2020 Nutrition Guideline",
        "text": "KDIGO 2020 Nutrition guidelines recommend: protein intake 0.6-0.8 g/kg/day for non-dialysis CKD stages 3-5; 1.0-1.2 g/kg/day for dialysis patients. Sodium restriction <2g/day. Potassium restriction based on serum levels. Low phosphorus diet and phosphate binders when needed. Dietary referral to a renal dietitian is recommended for all CKD G3b+ patients.",
    },
    {
        "id": "metformin_ckd",
        "title": "Metformin in CKD",
        "source": "FDA Guidelines & KDIGO 2022",
        "text": "Metformin use in CKD: Continue in eGFR â‰¥45; use with caution and at reduced dose in eGFR 30-44; contraindicated in eGFR <30 due to risk of lactic acidosis. Metformin should be temporarily withheld before iodinated contrast procedures in CKD patients. Reassess after 48 hours following contrast if renal function stable.",
    },
    {
        "id": "nsaid_ckd",
        "title": "NSAIDs in CKD",
        "source": "Clinical Practice - Nephrotoxicity Review",
        "text": "NSAIDs should be avoided in patients with CKD (eGFR <60) as they reduce prostaglandin-mediated afferent arteriolar dilation, decreasing GFR and potentially precipitating acute kidney injury. In CKD patients requiring analgesia, paracetamol (acetaminophen) at appropriate doses is preferred. Opioids may be used with caution but require dose adjustment in CKD.",
    },
    {
        "id": "anaemia_ckd",
        "title": "Anaemia Management in CKD",
        "source": "KDIGO 2012 Anaemia Guideline (Updated 2024)",
        "text": "CKD-related anaemia primarily results from erythropoietin deficiency. ESA (Erythropoiesis-Stimulating Agents) therapy targets Hb 10-11.5 g/dL; avoid >13 g/dL. Iron deficiency must be corrected before/during ESA therapy (target ferritin >100 ng/mL, TSAT >20%). HIF-PHI (Roxadustat, Daprodustat) represent newer therapeutic options approved in some countries.",
    },
    {
        "id": "mineral_bone_ckd",
        "title": "CKD-Mineral Bone Disorder",
        "source": "KDIGO 2017 CKD-MBD Guideline",
        "text": "CKD-MBD develops as eGFR declines. Key abnormalities: hyperphosphatemia, hypocalcemia, elevated PTH, vitamin D deficiency, FGF-23 elevation. Management: dietary phosphate restriction, phosphate binders (calcium-based and non-calcium-based), active vitamin D (calcitriol/alfacalcidol), calcimimetics (cinacalcet) for secondary hyperparathyroidism. Monitor calcium, phosphorus, PTH every 3-12 months depending on CKD stage.",
    },
    {
        "id": "dialysis_adequacy",
        "title": "Dialysis Adequacy",
        "source": "KDOQI Hemodialysis Adequacy Guidelines",
        "text": "Minimum Kt/V of 1.2 per hemodialysis session (single-pool) is recommended. Thrice-weekly dialysis is standard. Kt/V <1.2 is associated with increased morbidity and mortality. Residual renal function should be preserved by avoiding nephrotoxic drugs and volume depletion. Peritoneal dialysis provides continuous solute clearance and may better preserve residual renal function.",
    },
    {
        "id": "economic_burden_india",
        "title": "Economic Burden of Hemodialysis â€” India",
        "source": "Published Research â€” South India Pharmacoeconomic Study",
        "text": "Maintenance hemodialysis creates significant economic burden for patients in rural India. Direct medical costs (dialysis, medications, labs) combined with indirect costs (caregiver time, wage loss, transportation) frequently exceed household income. Studies in South India document catastrophic health expenditure in >60% of hemodialysis patients. Government schemes (PMJAY, Aarogyasri) provide partial coverage but gaps remain significant. Quality of life, measured using KDQoL-SF, is markedly impaired across physical, emotional, and social domains.",
    },
    {
        "id": "ckd_dm_management",
        "title": "Diabetes Management in CKD",
        "source": "ADA Standards of Care 2024 / KDIGO Diabetes-CKD 2022",
        "text": "Target HbA1c ~7% in most CKD patients with diabetes; individualise targets (7-8%) for those with hypoglycaemia risk, limited life expectancy, or advanced CKD. SGLT2 inhibitors are preferred add-on therapy when eGFR â‰¥20. GLP-1 receptor agonists (semaglutide, liraglutide) provide cardiorenal benefits and are preferred second agents. Sulfonylureas have increased hypoglycaemia risk in CKD. Insulin doses may need reduction as GFR declines.",
    },
    {
        "id": "potassium_management_ckd",
        "title": "Hyperkalaemia in CKD",
        "source": "KDIGO 2023 Potassium Management",
        "text": "Hyperkalaemia (serum K+ >5.5 mEq/L) is common in CKD, especially with RAAS inhibitor use. Management includes: dietary potassium restriction (<2000-3000 mg/day based on stage), dietary counselling, novel potassium binders (patiromer, sodium zirconium cyclosilicate), loop diuretics. Avoid ACEi/ARB dose reduction/discontinuation if possible â€” use potassium binders to maintain RAAS therapy. Emergent hyperkalaemia (K+ >6.5 or ECG changes) requires immediate treatment.",
    },
]


class ClinicalRAGEngine:
    """
    Lightweight RAG engine for clinical evidence retrieval.
    Uses FAISS + sentence-transformers when available, falls back to keyword search.
    """

    def __init__(self):
        self.knowledge_base = BUILT_IN_KNOWLEDGE.copy()
        self.uploaded_chunks = []
        self._index = None
        self._embeddings = None
        self._model = None
        self._all_texts = []
        self._all_meta = []

        if FAISS_AVAILABLE and ST_AVAILABLE:
            self._init_vector_store()

    def _init_vector_store(self):
        try:
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            self._rebuild_index()
        except Exception:
            self._model = None

    def _rebuild_index(self):
        if not self._model:
            return
        all_items = self.knowledge_base + self.uploaded_chunks
        texts = [item["text"] for item in all_items]
        meta = [{"title": item.get("title", ""), "source": item.get("source", ""), "text": item["text"]} for item in all_items]

        embeddings = self._model.encode(texts, show_progress_bar=False)
        import numpy as np
        embeddings = np.array(embeddings, dtype="float32")
        faiss.normalize_L2(embeddings)

        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)

        self._index = index
        self._embeddings = embeddings
        self._all_texts = texts
        self._all_meta = meta

    def add_pdf(self, pdf_bytes: bytes, filename: str = "upload") -> int:
        """Parse PDF and add to knowledge base. Returns number of chunks added."""
        chunks = _extract_pdf_chunks(pdf_bytes, filename)
        self.uploaded_chunks.extend(chunks)
        if self._model:
            self._rebuild_index()
        return len(chunks)

    def search(self, query: str, top_k: int = 4) -> list[dict]:
        """Retrieve top_k most relevant chunks."""
        if self._model and self._index:
            return self._vector_search(query, top_k)
        return self._keyword_search(query, top_k)

    def _vector_search(self, query: str, top_k: int) -> list[dict]:
        import numpy as np
        q_emb = self._model.encode([query], show_progress_bar=False)
        q_emb = np.array(q_emb, dtype="float32")
        faiss.normalize_L2(q_emb)
        scores, indices = self._index.search(q_emb, min(top_k, len(self._all_meta)))
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:
                meta = self._all_meta[idx].copy()
                meta["score"] = float(score)
                results.append(meta)
        return results

    def _keyword_search(self, query: str, top_k: int) -> list[dict]:
        query_words = set(query.lower().split())
        scored = []
        all_items = self.knowledge_base + self.uploaded_chunks
        for item in all_items:
            text_lower = item["text"].lower() + " " + item.get("title", "").lower()
            matches = sum(1 for w in query_words if w in text_lower)
            if matches > 0:
                scored.append({
                    "title": item.get("title", ""),
                    "source": item.get("source", ""),
                    "text": item["text"],
                    "score": matches / len(query_words),
                })
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def answer_query(self, query: str) -> dict:
        """Full RAG pipeline: retrieve â†’ generate answer."""
        retrieved = self.search(query, top_k=4)
        context = "\n\n".join(
            f"[{i+1}] **{r['title']}** ({r['source']})\n{r['text']}"
            for i, r in enumerate(retrieved)
        )

        prompt = f"""You are a Clinical Evidence AI assistant specialising in nephrology and CKD management.

User Clinical Question: {query}

Retrieved Evidence Context:
{context}

Based on the evidence above, provide:
1. **Evidence Summary** â€” 2-3 sentence direct answer to the clinical question
2. **Key Findings** â€” 3-4 bullet points of key clinical points
3. **Monitoring Considerations** â€” what should be monitored in this clinical context
4. **Clinical Considerations** â€” important caveats or clinical pearls

Use clinical language appropriate for nephrology professionals.
Always ground your answer in the provided evidence. Cite source numbers [1], [2] etc.

End with this exact disclaimer:
"âš•ï¸ *This system provides evidence-based insights and does not replace clinical judgment. Always consult current clinical guidelines and specialist opinion.*" """

        system = (
            "You are a board-certified clinical pharmacist and nephrology specialist AI. "
            "Provide evidence-based responses grounded in provided context. "
            "Be precise, cite evidence, and include appropriate clinical caveats."
        )

        ai_answer = get_ai_response(prompt, system, max_tokens=1200)

        if not ai_answer:
            ai_answer = _fallback_answer(query, retrieved)

        return {
            "query": query,
            "answer": ai_answer,
            "sources": retrieved,
            "sources_count": len(retrieved),
            "vector_search_used": self._model is not None,
        }

    def has_uploaded_documents(self) -> bool:
        return len(self.uploaded_chunks) > 0


def _extract_pdf_chunks(pdf_bytes: bytes, filename: str, chunk_size: int = 500) -> list[dict]:
    """Extract text from PDF and split into chunks."""
    full_text = ""
    if not PDF_AVAILABLE:
        return []
    try:
        import io
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            for page in reader.pages:
                full_text += page.extract_text() + "\n"
        except Exception:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(pdf_bytes))
            for page in reader.pages:
                full_text += page.extract_text() + "\n"
    except Exception:
        return []

    words = full_text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i:i + chunk_size]
        chunk_text = " ".join(chunk_words)
        if len(chunk_text.strip()) > 50:
            chunks.append({
                "id": f"upload_{filename}_{i}",
                "title": f"{filename} (p.{i//chunk_size + 1})",
                "source": filename,
                "text": chunk_text,
            })
    return chunks


def _fallback_answer(query: str, sources: list[dict]) -> str:
    if not sources:
        return (
            "No relevant evidence found in the knowledge base for this query. "
            "Please upload relevant clinical guidelines or research papers.\n\n"
            "âš•ï¸ *This system provides evidence-based insights and does not replace clinical judgment.*"
        )
    answer = "**Evidence Summary**\n\n"
    answer += "Based on the retrieved clinical evidence:\n\n"
    for i, s in enumerate(sources[:3], 1):
        answer += f"**[{i}] {s['title']}** ({s['source']})\n{s['text'][:300]}...\n\n"
    answer += "\nâš•ï¸ *This system provides evidence-based insights and does not replace clinical judgment.*"
    return answer


# Singleton instance
_rag_engine = None

def get_rag_engine() -> ClinicalRAGEngine:
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = ClinicalRAGEngine()
    return _rag_engine
