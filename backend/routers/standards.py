"""Standards router — browse and search the standards knowledge base."""

import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Standard
from schemas import StandardOut

router = APIRouter(prefix="/api", tags=["standards"])


@router.get("/standards", response_model=list[StandardOut])
async def list_standards(
    search: Optional[str] = Query(None, description="Search query"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    db: Session = Depends(get_db),
):
    """List all standards, optionally filtered by search query or sector."""
    query = db.query(Standard)

    if sector:
        query = query.filter(Standard.sector == sector)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            Standard.title.ilike(search_pattern)
            | Standard.is_number.ilike(search_pattern)
            | Standard.scope.ilike(search_pattern)
            | Standard.keywords.ilike(search_pattern)
        )

    standards = query.order_by(Standard.is_number).all()
    return standards


@router.get("/standards/sectors")
async def list_sectors(db: Session = Depends(get_db)):
    """Get distinct sectors from the standards database."""
    sectors = db.query(Standard.sector).distinct().filter(Standard.sector.isnot(None)).all()
    return [s[0] for s in sectors if s[0]]


@router.get("/standards/{standard_id}", response_model=StandardOut)
async def get_standard(
    standard_id: int,
    db: Session = Depends(get_db),
):
    """Get details for a specific standard."""
    standard = db.query(Standard).filter(Standard.id == standard_id).first()
    if not standard:
        raise HTTPException(status_code=404, detail="Standard not found.")
    return standard
