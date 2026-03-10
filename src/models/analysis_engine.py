import ollama
import requests


"""
analysis_engine.py
------------------
AI-powered frequency analysis using Ollama (local) -> Groq (cloud) -> built-in fallback.
Uses ollama.chat() pattern consistent with Jarvis Brain implementation.

Usage:
    from analysis_engine import generate_analysis
    result = generate_analysis(review_text)
"""

# ── Config ────────────────────────────────────────────────────────────────────
OLLAMA_MODEL = "phi3:mini"           # run: ollama pull phi3:mini

GROQ_API_KEY = "YOUR_GROQ_API_KEY"  # setup with keychain - DO NOT USE
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-8b-8192"
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a knowledgeable and empathetic frequency analyst specializing in
chakra systems, solfeggio frequencies, and sound healing.

Given a plain-text frequency detection summary from a real-time audio analyzer, produce a
rich, structured interpretation with:

1. A warm 2-3 paragraph Overall Energy Profile — speak directly to the user
2. Key Activations — for each detected frequency: emoji, name, activation level,
   and a 1-2 sentence personalized interpretation
3. Dominant Pattern — 2-3 sentences summarizing the overall energetic theme
4. Practical Suggestions — 2-3 actionable recommendations (meditation focus,
   complementary frequencies, activities that match this energy profile)

Tone: Warm, grounded, insightful — not overly mystical.
Format: Clean markdown with headers and bullet points.
Do not just restate the percentages — interpret what they mean for the person."""


def _call_ollama(review_text: str) -> str | None:
    """Call local Ollama using ollama.chat() — same pattern as Jarvis Brain."""
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Analyze this frequency session:\n\n{review_text}"}
            ],
            options={
                "temperature": 0.7,
                "num_predict": 800,
                "num_ctx": 2048,
            }
        )
        return response["message"]["content"]
    except Exception as e:
        print(f"[AnalysisEngine] Ollama unavailable: {e}")
        return None


def _call_groq(review_text: str) -> str | None:
    """Fall back to Groq cloud API if Ollama is not running."""
    if GROQ_API_KEY == "YOUR_GROQ_API_KEY":
        print("[AnalysisEngine] Groq not configured, skipping.")
        return None
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Analyze this frequency session:\n\n{review_text}"}
            ],
            "max_tokens": 800
        }
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"[AnalysisEngine] Groq error: {response.status_code}")
    except Exception as e:
        print(f"[AnalysisEngine] Groq unavailable: {e}")
    return None


def _builtin_fallback(review_text: str) -> str:
    """Last resort — return the original summary with a note."""
    return (
        "⚠️ AI analysis unavailable (Ollama not running, Groq not configured).\n\n"
        + review_text.replace("REVIEW TEXT: ", "")
    )


def generate_analysis(review_text: str) -> str:
    """
    Main entry point. Returns AI-generated analysis as a markdown string.
    Tries Ollama -> Groq -> built-in fallback automatically.

    Args:
        review_text: The full review string from your FFT app

    Returns:
        Markdown-formatted analysis string
    """
    # 1. Try local Ollama
    print("[AnalysisEngine] Trying Ollama...")
    result = _call_ollama(review_text)
    if result:
        print("[AnalysisEngine] Handled by Ollama")
        return result

    # 2. Try Groq
    print("[AnalysisEngine] Trying Groq...")
    result = _call_groq(review_text)
    if result:
        print("[AnalysisEngine] Handled by Groq")
        return result

    # 3. Built-in fallback
    print("[AnalysisEngine] Using built-in fallback")
    return _builtin_fallback(review_text)


def check_backends() -> dict:
    """
    Call on app startup to know what's available.
    Returns dict with status of each backend.
    """
    status = {"ollama": False, "groq": False}

    try:
        requests.get("http://localhost:11434", timeout=3)
        status["ollama"] = True
    except Exception:
        pass

    status["groq"] = GROQ_API_KEY != "YOUR_GROQ_API_KEY"

    print(f"[AnalysisEngine] Backends — Ollama: {status['ollama']} | Groq: {status['groq']}")
    return status
