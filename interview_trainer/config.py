"""
Central configuration for Interview Trainer Agent.

All tuneable constants live here. Override with environment variables or a
.env file placed in the project root (see .env.example).
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
# __file__ is interview_trainer/config.py → parent is interview_trainer/
PROJECT_ROOT: Path = Path(__file__).parent
KNOWLEDGE_BASE_DIR: Path = PROJECT_ROOT / "knowledge_base"
DB_PATH: Path = PROJECT_ROOT / "interview_trainer.db"

# Load .env – check multiple locations so the app works from any working directory.
# Also falls back to .env.example so users can fill credentials there directly.
_env_candidates = [
    PROJECT_ROOT / ".env",            # interview_trainer/.env  (preferred)
    PROJECT_ROOT.parent / ".env",     # workspace root .env
    PROJECT_ROOT / ".env.example",    # interview_trainer/.env.example (dev fallback)
    PROJECT_ROOT.parent / ".env.example",  # workspace root .env.example
]
for _env_path in _env_candidates:
    if _env_path.exists():
        load_dotenv(_env_path)
        break
else:
    load_dotenv()  # last resort: let python-dotenv search CWD

# ---------------------------------------------------------------------------
# IBM watsonx.ai credentials  – read from environment only, never hardcoded
# ---------------------------------------------------------------------------
WATSONX_API_KEY: str = os.environ.get("WATSONX_API_KEY", "")
WATSONX_URL: str = os.environ.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_PROJECT_ID: str = os.environ.get("WATSONX_PROJECT_ID", "")

# Default Granite model – ibm/granite-4-h-small is the IBM Granite generation model
# available on the Lite plan that supports the text generation API.
# Override via WATSONX_MODEL_ID env var if your project has a different version.
WATSONX_MODEL_ID: str = os.environ.get(
    "WATSONX_MODEL_ID", "ibm/granite-4-h-small"
)

# ---------------------------------------------------------------------------
# LLM generation parameters
# ---------------------------------------------------------------------------
LLM_MAX_NEW_TOKENS: int = 1024
LLM_TEMPERATURE: float = 0.3
LLM_TOP_P: float = 0.9
LLM_REPETITION_PENALTY: float = 1.1
LLM_TIMEOUT_SECONDS: int = 60
LLM_MAX_RETRIES: int = 3

# ---------------------------------------------------------------------------
# RAG / embedding parameters
# ---------------------------------------------------------------------------
EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
RETRIEVAL_TOP_K: int = 5
CHUNK_SIZE: int = 512          # approximate characters per chunk
CHUNK_OVERLAP: int = 64

# ---------------------------------------------------------------------------
# Supported roles  (maps display name -> knowledge-base file stem)
# ---------------------------------------------------------------------------
SUPPORTED_ROLES: dict[str, str] = {
    "Java Developer": "java_developer",
    "AI/ML Engineer": "ai_ml_engineer",
    "Data Analyst": "data_analyst",
    "Frontend Developer": "frontend_developer",
    "DevOps Engineer": "devops_engineer",
    "Product Manager": "product_manager",
}

EXPERIENCE_LEVELS: list[str] = ["Fresher", "0-2 yrs", "2-5 yrs", "5+ yrs"]

INTERVIEW_TYPES: list[str] = ["Technical", "Soft Skills", "Mixed"]

COMPANY_TYPES: list[str] = [
    "Any",
    "Service Company",
    "Product Company",
    "Startup",
    "Bank / BFSI",
]

# ---------------------------------------------------------------------------
# Evaluation rubric dimensions
# ---------------------------------------------------------------------------
RUBRIC_DIMENSIONS: list[str] = [
    "clarity",
    "correctness",
    "depth",
    "structure",
    "communication",
]
