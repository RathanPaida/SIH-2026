"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# --- Standards ---
class StandardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_number: str
    title: str
    year: Optional[int] = None
    scope: Optional[str] = None
    keywords: Optional[str] = None
    sector: Optional[str] = None


# --- Requirements ---
class RequirementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tender_id: int
    req_type: str
    description: str
    keywords: Optional[str] = None


# --- Extraction ---
class ExtractRequest(BaseModel):
    text: Optional[str] = None  # raw pasted text (file upload handled via Form)


class ExtractedRequirement(BaseModel):
    req_type: str
    description: str
    keywords: list[str]


class ExtractResponse(BaseModel):
    tender_id: int
    title: str
    requirements: list[RequirementOut]


# --- Recommendations ---
class RecommendRequest(BaseModel):
    tender_id: int


class RecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    requirement_id: int
    standard_id: int
    relevance_score: float
    justification: Optional[str] = None
    standard: StandardOut
    decision: Optional[str] = None
    officer_notes: Optional[str] = None


class RecommendResponse(BaseModel):
    tender_id: int
    requirements: list[dict]  # Each has requirement + recommendations


# --- Review ---
class ReviewRequest(BaseModel):
    decision: str  # "accept", "reject", "flag"
    officer_notes: Optional[str] = None


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recommendation_id: int
    decision: str
    officer_notes: Optional[str] = None
    decided_at: Optional[datetime] = None


# --- Export ---
class ExportRequest(BaseModel):
    tender_id: int
    format: str = "pdf"  # "pdf" or "docx"


# --- Tender ---
class TenderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: Optional[str] = None
    title: Optional[str] = None
    created_at: Optional[datetime] = None
    requirement_count: int = 0

