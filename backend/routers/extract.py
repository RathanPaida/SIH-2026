"""Extract router — POST /api/extract

Accepts a file upload (PDF/DOCX/TXT) or raw text.
Parses the document, extracts requirements via LLM, and persists to DB.
"""

import json
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Tender, Requirement
from schemas import ExtractResponse, RequirementOut
from services.document_parser import extract_text
from services.llm_service import extract_requirements

router = APIRouter(prefix="/api", tags=["extraction"])


@router.post("/extract", response_model=ExtractResponse)
async def extract_tender_requirements(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Extract technical/performance/safety requirements from a tender document.

    Accepts either:
    - A file upload (PDF, DOCX, or TXT)
    - Raw text pasted via the 'text' field
    """
    raw_text = ""
    filename = None

    if file and file.filename:
        # Process uploaded file
        file_bytes = await file.read()
        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        try:
            raw_text = extract_text(file_bytes, file.filename)
            filename = file.filename
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    elif text and text.strip():
        raw_text = text.strip()
        filename = "pasted_text.txt"
    else:
        raise HTTPException(
            status_code=400,
            detail="Please provide either a file upload or text content.",
        )

    if len(raw_text) < 50:
        raise HTTPException(
            status_code=400,
            detail="Text too short. Please provide a more detailed tender document.",
        )

    # Extract requirements via LLM (or mock)
    try:
        result = extract_requirements(raw_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Requirement extraction failed: {str(e)}")

    title = result.get("title", "Untitled Tender")
    extracted_reqs = result.get("requirements", [])

    if not extracted_reqs:
        raise HTTPException(
            status_code=422,
            detail="No requirements could be extracted from the document. Please try a more detailed tender text.",
        )

    # Persist tender
    tender = Tender(
        filename=filename,
        raw_text=raw_text[:50000],  # Limit stored text
        title=title,
    )
    db.add(tender)
    db.flush()

    # Persist requirements
    req_models = []
    for req in extracted_reqs:
        keywords = req.get("keywords", [])
        if isinstance(keywords, list):
            keywords = json.dumps(keywords)
        requirement = Requirement(
            tender_id=tender.id,
            req_type=req.get("req_type", "technical"),
            description=req.get("description", ""),
            keywords=keywords,
        )
        db.add(requirement)
        req_models.append(requirement)

    db.commit()
    db.refresh(tender)

    # Build response
    req_out = []
    for r in req_models:
        db.refresh(r)
        req_out.append(RequirementOut(
            id=r.id,
            tender_id=r.tender_id,
            req_type=r.req_type,
            description=r.description,
            keywords=r.keywords,
        ))

    return ExtractResponse(
        tender_id=tender.id,
        title=title,
        requirements=req_out,
    )
