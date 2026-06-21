"""Shared helper functions for RenalCare AI."""
import os
import sys
from pathlib import Path
from typing import Optional

# Ensure project root is on path
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_env():
    """Load from .env file (local) or Streamlit secrets (cloud)."""
    try:
        from dotenv import load_dotenv
        env_path = ROOT / ".env"
        if env_path.exists():
            load_dotenv(env_path)
    except ImportError:
        pass
    # Streamlit Cloud secrets â†’ env vars
    try:
        import streamlit as st
        for key in ["OPENAI_API_KEY", "GOOGLE_API_KEY"]:
            if key in st.secrets and not os.getenv(key):
                os.environ[key] = st.secrets[key]
    except Exception:
        pass


def get_openai_client():
    """Return configured OpenAI client or None."""
    load_env()
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key.startswith("sk-your"):
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    except Exception:
        return None


def get_gemini_model():
    """Return configured Gemini model or None."""
    load_env()
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key or api_key == "your-google-gemini-key-here":
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        return None


def get_ai_response(prompt: str, system: str = "", max_tokens: int = 1500) -> str:
    """Get AI response from OpenAI, Gemini, or fallback."""
    client = get_openai_client()
    if client:
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.3,
            )
            return resp.choices[0].message.content
        except Exception as e:
            pass

    model = get_gemini_model()
    if model:
        try:
            full_prompt = f"{system}\n\n{prompt}" if system else prompt
            resp = model.generate_content(full_prompt)
            return resp.text
        except Exception:
            pass

    return None


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate BMI."""
    if height_cm <= 0:
        return 0.0
    return round(weight_kg / ((height_cm / 100) ** 2), 1)


def classify_bmi(bmi: float) -> tuple[str, str]:
    """Return (category, color) for BMI."""
    if bmi < 18.5:
        return "Underweight", "#3498db"
    elif bmi < 25:
        return "Normal", "#27ae60"
    elif bmi < 30:
        return "Overweight", "#f39c12"
    else:
        return "Obese", "#e74c3c"


def get_ckd_stage(egfr: float) -> dict:
    """Return CKD stage info dict for given eGFR."""
    from utils.constants import CKD_STAGES
    if egfr >= 90:
        return {**CKD_STAGES[1], "stage_num": 1}
    elif egfr >= 60:
        return {**CKD_STAGES[2], "stage_num": 2}
    elif egfr >= 45:
        return {**CKD_STAGES[3], "stage_num": "3a"}
    elif egfr >= 30:
        return {**CKD_STAGES[4], "stage_num": "3b"}
    elif egfr >= 15:
        return {**CKD_STAGES[5], "stage_num": 4}
    else:
        return {**CKD_STAGES[6], "stage_num": 5}


def format_currency(amount: float, currency: str = "INR") -> str:
    """Format number as currency string."""
    if currency == "INR":
        return f"â‚¹{amount:,.0f}"
    return f"${amount:,.0f}"


def classify_risk_score(score: float) -> str:
    """Classify a 0-100 risk score into Low/Moderate/High/Critical."""
    if score < 25:
        return "Low"
    elif score < 50:
        return "Moderate"
    elif score < 75:
        return "High"
    else:
        return "Critical"
