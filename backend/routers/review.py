"""Review router — officer accept/reject/flag decisions on recommendations."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import datetime

from database import get_db
from models import Recommendation, ReviewDecision, Requirement, Tender, Standard
from schemas import ReviewRequest, ReviewOut

router = APIRouter(prefix="/api", tags=["review"])


@router.put("/review/{recommendation_id}", response_model=ReviewOut)
async def update_review_decision(
    recommendation_id: int,
    request: ReviewRequest,
    db: Session = Depends(get_db),
):
    """Accept, reject, or flag a recommended standard."""
    if request.decision not in ("accept", "reject", "flag"):
        raise HTTPException(status_code=400, detail="Decision must be 'accept', 'reject', or 'flag'.")

    recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found.")

    # Upsert review decision
    review = db.query(ReviewDecision).filter(
        ReviewDecision.recommendation_id == recommendation_id
    ).first()

    if review:
        review.decision = request.decision
        review.officer_notes = request.officer_notes
        review.decided_at = datetime.datetime.utcnow()
    else:
        review = ReviewDecision(
            recommendation_id=recommendation_id,
            decision=request.decision,
            officer_notes=request.officer_notes,
        )
        db.add(review)

    db.commit()
    db.refresh(review)

    return ReviewOut(
        id=review.id,
        recommendation_id=review.recommendation_id,
        decision=review.decision,
        officer_notes=review.officer_notes,
        decided_at=review.decided_at,
    )


@router.get("/tenders/{tender_id}/review")
async def get_tender_review(
    tender_id: int,
    db: Session = Depends(get_db),
):
    """Get all recommendations and their review status for a tender."""
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found.")

    requirements = db.query(Requirement).filter(Requirement.tender_id == tender_id).all()

    result = []
    for req in requirements:
        recommendations = db.query(Recommendation).filter(
            Recommendation.requirement_id == req.id
        ).all()

        rec_list = []
        for rec in recommendations:
            standard = db.query(Standard).filter(Standard.id == rec.standard_id).first()
            review = db.query(ReviewDecision).filter(
                ReviewDecision.recommendation_id == rec.id
            ).first()

            rec_list.append({
                "id": rec.id,
                "standard_id": rec.standard_id,
                "is_number": standard.is_number if standard else "",
                "title": standard.title if standard else "",
                "scope": standard.scope if standard else "",
                "sector": standard.sector if standard else "",
                "relevance_score": rec.relevance_score,
                "justification": rec.justification,
                "decision": review.decision if review else None,
                "officer_notes": review.officer_notes if review else None,
            })

        result.append({
            "requirement_id": req.id,
            "req_type": req.req_type,
            "description": req.description,
            "keywords": req.keywords,
            "recommendations": rec_list,
        })

    return {
        "tender_id": tender_id,
        "title": tender.title,
        "filename": tender.filename,
        "created_at": str(tender.created_at) if tender.created_at else None,
        "requirements": result,
    }
