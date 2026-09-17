"""Application configuration loaded from environment variables."""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "manak_mitra.db"
SEED_DIR = BASE_DIR / "seed"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Whether to use real LLM or mock fallback
USE_MOCK_LLM = not bool(OPENAI_API_KEY)

# Server
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))

# Embedding model for search (runs locally via sentence-transformers)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Search weights
FAISS_WEIGHT = 0.6
BM25_WEIGHT = 0.4
TOP_K_RESULTS = 5
