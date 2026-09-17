"""SQLAlchemy ORM models for Manak Mitra."""

import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from database import Base
import enum


class DecisionType(str, enum.Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    FLAG = "flag"


class Tender(Base):
    __tablename__ = "tenders"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=True)
    raw_text = Column(Text, nullable=False)
    title = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    requirements = relationship("Requirement", back_populates="tender", cascade="all, delete-orphan")


class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("tenders.id"), nullable=False)
    req_type = Column(String(100), nullable=False)  # e.g., "technical", "performance", "safety"
    description = Column(Text, nullable=False)
    keywords = Column(Text, nullable=True)  # JSON array stored as text

    tender = relationship("Tender", back_populates="requirements")
    recommendations = relationship("Recommendation", back_populates="requirement", cascade="all, delete-orphan")


class Standard(Base):
    __tablename__ = "standards"

    id = Column(Integer, primary_key=True, index=True)
    is_number = Column(String(50), unique=True, nullable=False)  # e.g., "IS 269:2015"
    title = Column(String(500), nullable=False)
    year = Column(Integer, nullable=True)
    scope = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)  # JSON array stored as text
    sector = Column(String(100), nullable=True)

    recommendations = relationship("Recommendation", back_populates="standard")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=False)
    standard_id = Column(Integer, ForeignKey("standards.id"), nullable=False)
    relevance_score = Column(Float, nullable=False)
    justification = Column(Text, nullable=True)

    requirement = relationship("Requirement", back_populates="recommendations")
    standard = relationship("Standard", back_populates="recommendations")
    review_decision = relationship("ReviewDecision", back_populates="recommendation", uselist=False, cascade="all, delete-orphan")


class ReviewDecision(Base):
    __tablename__ = "review_decisions"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), unique=True, nullable=False)
    decision = Column(String(20), nullable=False)  # accept, reject, flag
    officer_notes = Column(Text, nullable=True)
    decided_at = Column(DateTime, default=datetime.datetime.utcnow)

    recommendation = relationship("Recommendation", back_populates="review_decision")
