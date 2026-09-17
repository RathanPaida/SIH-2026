"""Recommend router — POST /api/recommend

Takes a tender_id, runs hybrid search for each requirement,
generates relevance justifications, and persists recommendations.
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Tender, Requirement, Recommendation, Standard, ReviewDecision
from schemas import RecommendRequest, RecommendResponse
from services.search_service import hybrid_search, is_index_ready
from services.llm_service import generate_justification
from config import TOP_K_RESULTS

router = APIRouter(prefix="/api", tags=["recommendations"])


@router.post("/recommend", response_model=RecommendResponse)
async def recommend_standards(
    request: RecommendRequest,
    db: Session = Depends(get_db),
):
    """
    For each requirement in the tender, search the standards knowledge base
    and return ranked candidate Indian Standards with relevance scores.
    """
    tender = db.query(Tender).filter(Tender.id == request.tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found.")

    requirements = db.query(Requirement).filter(Requirement.tender_id == request.tender_id).all()
    if not requirements:
        raise HTTPException(status_code=404, detail="No requirements found for this tender.")

    if not is_index_ready():
        raise HTTPException(status_code=503, detail="Search index not ready. Please wait and retry.")

    # Delete existing recommendations for this tender (allow re-run)
    existing_rec_ids = [
        r.id for r in db.query(Recommendation)
        .join(Requirement)
        .filter(Requirement.tender_id == request.tender_id)
        .all()
    ]
    if existing_rec_ids:
        db.query(ReviewDecision).filter(ReviewDecision.recommendation_id.in_(existing_rec_ids)).delete(synchronize_session=False)
        db.query(Recommendation).filter(Recommendation.id.in_(existing_rec_ids)).delete(synchronize_session=False)
        db.flush()

    result_requirements = []

    for req in requirements:
        # Build search query from description + keywords
        keywords_list = []
        if req.keywords:
            try:
                keywords_list = json.loads(req.keywords)
            except json.JSONDecodeError:
                keywords_list = [req.keywords]

        search_query = req.description + " " + " ".join(keywords_list)

        # Hybrid search
        search_results = hybrid_search(search_query, top_k=TOP_K_RESULTS)

        req_recommendations = []
        for result in search_results:
            # Generate justification
            justification = generate_justification(
                requirement=req.description,
                std_number=result["is_number"],
                std_title=result["title"],
                std_scope=result.get("scope", ""),
            )

            # Find or verify standard in DB
            standard = db.query(Standard).filter(Standard.id == result["standard_id"]).first()
            if not standard:
                continue

            # Persist recommendation
            recommendation = Recommendation(
                requirement_id=req.id,
                standard_id=standard.id,
                relevance_score=result["score"],
                justification=justification,
            )
            db.add(recommendation)
            db.flush()

            req_recommendations.append({
                "id": recommendation.id,
                "standard_id": standard.id,
                "is_number": standard.is_number,
                "title": standard.title,
                "scope": standard.scope,
                "sector": standard.sector,
                "relevance_score": result["score"],
                "justification": justification,
                "decision": None,
                "officer_notes": None,
            })

        result_requirements.append({
            "requirement_id": req.id,
            "req_type": req.req_type,
            "description": req.description,
            "keywords": req.keywords,
            "recommendations": req_recommendations,
        })

    db.commit()

    return RecommendResponse(
        tender_id=request.tender_id,
        requirements=result_requirements,
    )
