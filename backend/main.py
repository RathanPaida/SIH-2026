"""
Manak Mitra — AI-Powered Indian Standards Recommender for Procurement Tenders

FastAPI backend application.
"""

import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from config import BACKEND_HOST, BACKEND_PORT
from database import init_db, SessionLocal
from models import Standard, Tender


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    # Startup
    print("=" * 60)
    print("  Manak Mitra Backend -- Starting up...")
    print("=" * 60)

    # 1. Initialize database tables
    init_db()
    print("[Startup] Database tables created.")

    # 2. Seed standards if needed
    from seed_db import seed_standards
    seed_standards()

    # 3. Build search index
    print("[Startup] Building search index (this may take a moment on first run)...")
    from services.search_service import build_index
    db = SessionLocal()
    try:
        standards = db.query(Standard).all()
        standards_dicts = [
            {
                "id": s.id,
                "is_number": s.is_number,
                "title": s.title,
                "scope": s.scope or "",
                "keywords": s.keywords or "[]",
                "sector": s.sector or "",
            }
            for s in standards
        ]
        build_index(standards_dicts)
    finally:
        db.close()

    from config import USE_MOCK_LLM
    if USE_MOCK_LLM:
        print("[Startup] WARNING: No OPENAI_API_KEY set -- using MOCK LLM mode.")
    else:
        print("[Startup] LLM integration active.")

    print("=" * 60)
    print(f"  Manak Mitra Backend ready at http://localhost:{BACKEND_PORT}")
    print("=" * 60)

    yield

    # Shutdown
    print("[Shutdown] Manak Mitra Backend shutting down.")


# Create FastAPI app
app = FastAPI(
    title="Manak Mitra API",
    description="AI-powered Indian Standards recommender for procurement tender specifications.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
from routers.extract import router as extract_router
from routers.recommend import router as recommend_router
from routers.review import router as review_router
from routers.standards import router as standards_router
from routers.export import router as export_router

app.include_router(extract_router)
app.include_router(recommend_router)
app.include_router(review_router)
app.include_router(standards_router)
app.include_router(export_router)


# --- Additional utility endpoints ---

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": "Manak Mitra",}


@app.get("/api/tenders")
async def list_tenders():
    """List all tenders with requirement counts."""
    db = SessionLocal()
    try:
        tenders = db.query(Tender).order_by(Tender.created_at.desc()).all()
        result = []
        for t in tenders:
            result.append({
                "id": t.id,
                "filename": t.filename,
                "title": t.title,
                "created_at": str(t.created_at) if t.created_at else None,
                "requirement_count": len(t.requirements),
            })
        return result
    finally:
        db.close()


@app.get("/api/sample-tenders")
async def get_sample_tenders():
    """Return sample tender texts for demo purposes."""
    from pathlib import Path
    sample_dir = Path(__file__).parent / "seed" / "sample_tenders"
    samples = []
    if sample_dir.exists():
        for f in sorted(sample_dir.glob("*.txt")):
            samples.append({
                "filename": f.name,
                "title": f.stem.replace("_", " ").title(),
                "text": f.read_text(encoding="utf-8"),
            })
    return samples


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=BACKEND_HOST, port=int(BACKEND_PORT), reload=True)
