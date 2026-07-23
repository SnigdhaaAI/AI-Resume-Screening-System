"""
Pydantic schemas used for request validation and API responses.
"""
from typing import List, Optional
import datetime as dt

from pydantic import BaseModel, Field, ConfigDict


# ---------- Job Description ----------

class JobDescriptionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    company: Optional[str] = None
    raw_text: str = Field(..., min_length=20, description="Full job description text")
    min_experience_years: Optional[float] = None


class JobDescriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company: Optional[str]
    required_skills: Optional[List[str]] = None
    min_experience_years: Optional[float] = None
    created_at: dt.datetime


# ---------- Resume ----------

class ResumeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_name: Optional[str]
    file_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    extracted_skills: Optional[List[str]] = None
    experience_years: Optional[float] = None
    created_at: dt.datetime


# ---------- Matching / Ranking ----------

class MatchResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    resume_id: int
    candidate_name: Optional[str] = None
    file_name: Optional[str] = None
    overall_score: float
    semantic_score: float
    skill_score: float
    experience_score: float
    matched_skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None
    explanation: Optional[str] = None
    rank: Optional[int] = None


class ScreeningRequest(BaseModel):
    job_id: int
    resume_ids: Optional[List[int]] = Field(
        default=None,
        description="Specific resume IDs to screen against the job. If omitted, all resumes are screened.",
    )
    top_k: Optional[int] = Field(default=None, description="Return only the top K candidates")


class ScreeningResponse(BaseModel):
    job_id: int
    job_title: str
    total_candidates: int
    results: List[MatchResultOut]
