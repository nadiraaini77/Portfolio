"""
Central configuration for the AI KTP app.

All environment-dependent values live here so nothing else in the codebase
reads os.environ directly. To swap the vision model, change MODEL_CLASSIFICATION
/ MODEL_OCR in your .env file (or export them as env vars) — no code changes needed.
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed yet — fine, real env vars still work
    pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --- OpenRouter ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Optional but recommended by OpenRouter for attribution/rate-limit tiers.
APP_SITE_URL = os.getenv("APP_SITE_URL", "http://localhost:8501")
APP_NAME = os.getenv("APP_NAME", "AI KTP Classifier & OCR")

# --- Model selection (swappable without touching code) ---
# Any vision-capable OpenRouter model slug works here, e.g.:
#   "google/gemini-2.0-flash-001"   (cheap, fast — good default)
#   "openai/gpt-4o"                 (stronger on messy/rotated photos)
#   "anthropic/claude-3.5-sonnet"   (stronger, pricier)
MODEL_CLASSIFICATION = os.getenv("MODEL_CLASSIFICATION", "google/gemini-2.0-flash-001")
MODEL_OCR = os.getenv("MODEL_OCR", "google/gemini-2.0-flash-001")

# --- Database ---
DB_PATH = os.getenv("DB_PATH", str(PROJECT_ROOT / "data" / "database.db"))

# --- Misc ---
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "60"))


def require_api_key() -> None:
    """Call this before making any OpenRouter request to fail with a clear error."""
    if not OPENROUTER_API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Add it to your .env file "
            "(copy .env.example to .env and fill it in)."
        )
