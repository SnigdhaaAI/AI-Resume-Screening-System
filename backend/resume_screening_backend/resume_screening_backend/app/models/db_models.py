"""
ORM models for jobs, resumes, and match results.
Embeddings are stored as JSON-serialized float lists for portability (SQLite has no native vector type).
"""
import datetime as dt

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
)
from sqlalchemy.orm import relationship

from app.database import Base


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    raw_text = Column(Text, nullable=False)
    cleaned_text = Column(Text, nullable=True)
    required_skills = Column(JSON, nullable=True)       # list[str]
    min_experience_years = Column(Float, nullable=True)
    embedding = Column(JSON, nullable=True)              # list[float]
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    matches = relationship("MatchResult", back_populates="job", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String(255), nullable=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    raw_text = Column(Text, nullable=False)
    cleaned_text = Column(Text, nullable=True)
    extracted_skills = Column(JSON, nullable=True)       # list[str]
    experience_years = Column(Float, nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    embedding = Column(JSON, nullable=True)              # list[float]
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    matches = relationship("MatchResult", back_populates="resume", cascade="all, delete-orphan")


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)

    overall_score = Column(Float, nullable=False)         # 0-100
    semantic_score = Column(Float, nullable=False)         # 0-100
    skill_score = Column(Float, nullable=False)             # 0-100
    experience_score = Column(Float, nullable=False)        # 0-100

    matched_skills = Column(JSON, nullable=True)            # list[str]
    missing_skills = Column(JSON, nullable=True)            # list[str]
    explanation = Column(Text, nullable=True)

    rank = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    job = relationship("JobDescription", back_populates="matches")
    resume = relationship("Resume", back_populates="matches")
