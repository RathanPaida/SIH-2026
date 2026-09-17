"""Export router — generate downloadable PDF or DOCX reports."""

import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from database import get_db
from models import Tender, Requirement, Recommendation, ReviewDecision, Standard
from schemas import ExportRequest
from services.export_service import generate_pdf_report, generate_docx_report

router = APIRouter(prefix="/api", tags=["export"])


@router.post("/export")
async def export_approved_standards(
    request: ExportRequest,
    db: Session = Depends(get_db),
):
    """
    Export a report of approved standards for a tender.
    Only includes recommendations with 'accept' decision (or all if none reviewed).
    """
    tender = db.query(Tender).filter(Tender.id == request.tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found.")

    requirements = db.query(Requirement).filter(
        Requirement.tender_id == request.tender_id
    ).all()

    if not requirements:
        raise HTTPException(status_code=404, detail="No requirements found for this tender.")

    # Check if any reviews exist
    has_reviews = False
    mappings = []

    for req in requirements:
        recommendations = db.query(Recommendation).filter(
            Recommendation.requirement_id == req.id
        ).all()

        approved_standards = []
        for rec in recommendations:
            review = db.query(ReviewDecision).filter(
                ReviewDecision.recommendation_id == rec.id
            ).first()

            if review:
                has_reviews = True

            # Include if accepted, or if no reviews exist yet (include all)
            if not review or review.decision == "accept":
                standard = db.query(Standard).filter(Standard.id == rec.standard_id).first()
                if standard:
                    approved_standards.append({
                        "is_number": standard.is_number,
                        "title": standard.title,
                        "justification": rec.justification or "",
                    })

        mappings.append({
            "requirement": req.description,
            "req_type": req.req_type,
            "standards": approved_standards,
        })

    tender_title = tender.title or tender.filename or f"Tender #{tender.id}"

    if request.format == "docx":
        content = generate_docx_report(tender_title, mappings)
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename=manak_mitra_report_{tender.id}.docx"},
        )
    else:
        content = generate_pdf_report(tender_title, mappings)
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=manak_mitra_report_{tender.id}.pdf"},
        )
