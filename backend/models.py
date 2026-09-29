"""SQLAlchemy ORM models for Manak Mitra.

Full data model covering standards lifecycle, QCOs, relations,
analysis pipeline, findings, audit trail, and feedback loop.
"""

import datetime
import enum
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey,
    Boolean, JSON, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from database import Base


# ─── Enums ──────────────────────────────────────────────

class StandardStatus(str, enum.Enum):
    CURRENT = "current"
    AMENDED = "amended"
    SUPERSEDED = "superseded"
    WITHDRAWN = "withdrawn"
    UNDER_REVISION = "under_revision"


class DecisionType(str, enum.Enum):
    APPROVE = "approve"
    MODIFY = "modify"
    REJECT = "reject"
    UNCERTAIN = "uncertain"


class FindingKind(str, enum.Enum):
    GAP = "gap"
    CONFLICT = "conflict"
    RISK = "risk"
    OUTDATED = "outdated"
    UNVERIFIED = "unverified"


class FindingSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RelationType(str, enum.Enum):
    REFERENCES = "REFERENCES"
    TEST_METHOD_FOR = "TEST_METHOD_FOR"
    ALLIED_TO = "ALLIED_TO"
    SUPERSEDES = "SUPERSEDES"
    AMENDED_BY = "AMENDED_BY"
    CERTIFIED_UNDER = "CERTIFIED_UNDER"


class RecommendationRelationship(str, enum.Enum):
    PRIMARY = "primary"
    NORMATIVE = "normative"
    ALLIED = "allied"
    ALTERNATIVE = "alternative"


class RecommendationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    NEEDS_REVIEW = "needs_review"
    UNCERTAIN = "uncertain"


class AnalysisStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ─── Users ──────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, default="Procurement Officer")
    role = Column(String(50), nullable=False, default="officer")  # officer, admin
    language = Column(String(10), nullable=False, default="en")
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# ─── Standards & Lifecycle ─────────────────────────────

class Standard(Base):
    __tablename__ = "standards"
    id = Column(Integer, primary_key=True, index=True)
    is_number = Column(String(50), unique=True, nullable=False)
    part = Column(String(50), nullable=True)
    year = Column(Integer, nullable=True)
    title = Column(String(500), nullable=False)
    scope = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)  # JSON array as text
    domain = Column(String(100), nullable=True)  # renamed from sector
    sector = Column(String(100), nullable=True)  # keep for backward compat
    ics_code = Column(String(50), nullable=True)
    technical_committee = Column(String(200), nullable=True)
    status = Column(String(30), nullable=False, default="current")
    latest_edition_year = Column(Integer, nullable=True)
    source_url = Column(String(500), nullable=True)
    source_note = Column(String(200), nullable=True, default="sample")

    # Relationships
    versions = relationship("StandardVersion", back_populates="standard", foreign_keys="StandardVersion.standard_id", cascade="all, delete-orphan")
    amendments = relationship("Amendment", back_populates="standard", cascade="all, delete-orphan")
    clauses = relationship("Clause", back_populates="standard", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="standard")
    relations_from = relationship("StandardRelation", foreign_keys="StandardRelation.from_standard_id", back_populates="from_standard")
    relations_to = relationship("StandardRelation", foreign_keys="StandardRelation.to_standard_id", back_populates="to_standard")


class StandardVersion(Base):
    __tablename__ = "standard_versions"
    id = Column(Integer, primary_key=True, index=True)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(String(30), nullable=False, default="current")
    superseded_by_id = Column(Integer, ForeignKey("standards.id"), nullable=True)
    effective_date = Column(String(20), nullable=True)

    standard = relationship("Standard", back_populates="versions", foreign_keys=[standard_id])


class Amendment(Base):
    __tablename__ = "amendments"
    id = Column(Integer, primary_key=True, index=True)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    amendment_no = Column(Integer, nullable=False)
    date = Column(String(20), nullable=True)
    summary = Column(Text, nullable=True)

    standard = relationship("Standard", back_populates="amendments")


class QCO(Base):
    __tablename__ = "qcos"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False)
    product = Column(String(300), nullable=True)
    notification_ref = Column(String(100), nullable=True)
    effective_date = Column(String(20), nullable=True)
    certification_scheme = Column(String(100), nullable=True)  # ISI, CRS, etc.
    notes = Column(Text, nullable=True)

    standards = relationship("QCOStandard", back_populates="qco", cascade="all, delete-orphan")


class QCOStandard(Base):
    __tablename__ = "qco_standards"
    id = Column(Integer, primary_key=True, index=True)
    qco_id = Column(Integer, ForeignKey("qcos.id"), nullable=False)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)

    qco = relationship("QCO", back_populates="standards")
    standard = relationship("Standard")


class StandardRelation(Base):
    __tablename__ = "relations"
    id = Column(Integer, primary_key=True, index=True)
    from_standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    to_standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    relation_type = Column(String(30), nullable=False)  # REFERENCES, TEST_METHOD_FOR, etc.

    from_standard = relationship("Standard", foreign_keys=[from_standard_id], back_populates="relations_from")
    to_standard = relationship("Standard", foreign_keys=[to_standard_id], back_populates="relations_to")


class Clause(Base):
    __tablename__ = "clauses"
    id = Column(Integer, primary_key=True, index=True)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    clause_no = Column(String(50), nullable=True)
    text = Column(Text, nullable=False)

    standard = relationship("Standard", back_populates="clauses")


# ─── Analyses & Pipeline ───────────────────────────────

class Analysis(Base):
    """A complete analysis run — replaces the old Tender model."""
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    name = Column(String(500), nullable=True)
    source_type = Column(String(20), nullable=True)  # upload, text, sample
    language = Column(String(10), nullable=True, default="en")
    detected_languages = Column(Text, nullable=True)  # JSON array
    status = Column(String(20), nullable=False, default="queued")
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String(20), nullable=True)  # Low, Medium, High
    progress = Column(Integer, nullable=True, default=0)
    current_stage = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    # Options
    domain_hint = Column(String(50), nullable=True)
    use_reranker = Column(Boolean, default=False)
    include_allied = Column(Boolean, default=True)
    # Stats
    pages_count = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    requirements_count = Column(Integer, nullable=True, default=0)
    standards_count = Column(Integer, nullable=True, default=0)
    gaps_count = Column(Integer, nullable=True, default=0)
    conflicts_count = Column(Integer, nullable=True, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    document = relationship("Document", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    requirements = relationship("Requirement", back_populates="analysis", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="analysis", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="analysis", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="analysis", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    filename = Column(String(255), nullable=True)
    mime_type = Column(String(100), nullable=True)
    pages = Column(Integer, nullable=True)
    ocr_used = Column(Boolean, default=False)
    raw_text = Column(Text, nullable=True)

    analysis = relationship("Analysis", back_populates="document")
    blocks = relationship("Block", back_populates="document", cascade="all, delete-orphan")


class Block(Base):
    __tablename__ = "blocks"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    page = Column(Integer, nullable=True)
    order = Column(Integer, nullable=True)
    text_original = Column(Text, nullable=True)
    text_translated = Column(Text, nullable=True)
    lang = Column(String(10), nullable=True)
    ocr_confidence = Column(Float, nullable=True)
    kind = Column(String(30), nullable=True)  # heading, paragraph, table_row

    document = relationship("Document", back_populates="blocks")


# ─── Legacy Tender model (backward compat) ─────────────

class Tender(Base):
    __tablename__ = "tenders"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=True)
    raw_text = Column(Text, nullable=False)
    title = Column(String(500), nullable=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    requirements = relationship("Requirement", back_populates="tender", cascade="all, delete-orphan")


# ─── Requirements ──────────────────────────────────────

class Requirement(Base):
    __tablename__ = "requirements"
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("tenders.id"), nullable=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=True)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=True)
    code = Column(String(20), nullable=True)  # REQ-001, REQ-002...
    req_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    keywords = Column(Text, nullable=True)  # JSON array
    attributes_json = Column(Text, nullable=True)  # structured: product, property, value, unit, etc.
    confidence = Column(Float, nullable=True, default=0.8)
    source_page = Column(Integer, nullable=True)
    source_clause = Column(String(100), nullable=True)

    tender = relationship("Tender", back_populates="requirements")
    analysis = relationship("Analysis", back_populates="requirements")
    recommendations = relationship("Recommendation", back_populates="requirement", cascade="all, delete-orphan")


# ─── Recommendations ──────────────────────────────────

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=False)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    relationship_type = Column(String(30), nullable=True, default="primary")  # primary, normative, allied, alternative
    relevance_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=True)
    score_breakdown_json = Column(Text, nullable=True)  # {"lexical": 0.3, "semantic": 0.5, "graph": 0.2}
    status = Column(String(30), nullable=True, default="pending")  # pending, verified, needs_review, uncertain
    justification = Column(Text, nullable=True)
    evidence_json = Column(Text, nullable=True)  # matched terms, clause snippets, graph paths
    verification_json = Column(Text, nullable=True)  # lifecycle, edition, amendments, QCO checks
    correction_json = Column(Text, nullable=True)  # proposed corrections

    requirement = relationship("Requirement", back_populates="recommendations")
    standard = relationship("Standard", back_populates="recommendations")
    analysis = relationship("Analysis", back_populates="recommendations")
    review_decision = relationship("ReviewDecision", back_populates="recommendation", uselist=False, cascade="all, delete-orphan")


# ─── Review Decisions ─────────────────────────────────

class ReviewDecision(Base):
    __tablename__ = "review_decisions"
    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), unique=True, nullable=False)
    officer_id = Column(Integer, nullable=True)
    decision = Column(String(20), nullable=False)  # approve, modify, reject, uncertain
    comment = Column(Text, nullable=True)
    officer_notes = Column(Text, nullable=True)  # keep for backward compat
    previous_value = Column(Text, nullable=True)
    alternative_standard_id = Column(Integer, ForeignKey("standards.id"), nullable=True)
    decided_at = Column(DateTime, default=datetime.datetime.utcnow)

    recommendation = relationship("Recommendation", back_populates="review_decision")


# ─── Findings (Gaps, Conflicts, Risks) ────────────────

class Finding(Base):
    __tablename__ = "findings"
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    kind = Column(String(20), nullable=False)  # gap, conflict, risk, outdated, unverified
    severity = Column(String(20), nullable=False, default="medium")
    title = Column(String(300), nullable=True)
    description = Column(Text, nullable=False)
    requirement_ids = Column(Text, nullable=True)  # JSON array
    standard_ids = Column(Text, nullable=True)  # JSON array
    proposed_fix = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    analysis = relationship("Analysis", back_populates="findings")


# ─── Audit Log ─────────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=True)
    actor = Column(String(20), nullable=False, default="system")  # system, officer
    event = Column(String(200), nullable=False)
    detail = Column(Text, nullable=True)
    payload_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    analysis = relationship("Analysis", back_populates="audit_logs")


# ─── Feedback ──────────────────────────────────────────

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=True)
    signal = Column(String(20), nullable=True)  # accept, reject, modify
    payload_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
