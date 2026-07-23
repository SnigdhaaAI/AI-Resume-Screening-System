"""
Endpoints that run the screening pipeline: match resumes against a job
description, score them, rank them, and persist + return explainable results.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import db_models, schemas
from app.services import matching

router = APIRouter(prefix="/screening", tags=["Screening & Ranking"])


@router.post("/run", response_model=schemas.ScreeningResponse)
def run_screening(payload: schemas.ScreeningRequest, db: Session = Depends(get_db)):
    """
    Match a job description against one or more resumes, compute weighted
    similarity scores, rank candidates, and store the results.
    """
    job = db.query(db_models.JobDescription).filter(db_models.JobDescription.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    if not job.embedding:
        raise HTTPException(status_code=422, detail="Job description has no embedding; recreate it.")

    query = db.query(db_models.Resume)
    if payload.resume_ids:
        query = query.filter(db_models.Resume.id.in_(payload.resume_ids))
    resumes = query.all()

    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found to screen")

    # Clear any previous match results for this job to avoid stale duplicates
    db.query(db_models.MatchResult).filter(db_models.MatchResult.job_id == job.id).delete()

    computed = []
    for resume in resumes:
        if not resume.embedding:
            continue
        result = matching.compute_match(
            job_embedding=job.embedding,
            resume_embedding=resume.embedding,
            job_skills=job.required_skills or [],
            resume_skills=resume.extracted_skills or [],
            required_years=job.min_experience_years,
            candidate_years=resume.experience_years,
        )
        computed.append((resume, result))

    # Rank by overall score, descending
    computed.sort(key=lambda pair: pair[1]["overall_score"], reverse=True)

    if payload.top_k:
        computed = computed[: payload.top_k]

    output = []
    for idx, (resume, result) in enumerate(computed, start=1):
        match = db_models.MatchResult(
            job_id=job.id,
            resume_id=resume.id,
            overall_score=result["overall_score"],
            semantic_score=result["semantic_score"],
            skill_score=result["skill_score"],
            experience_score=result["experience_score"],
            matched_skills=result["matched_skills"],
            missing_skills=result["missing_skills"],
            explanation=result["explanation"],
            rank=idx,
        )
        db.add(match)
        db.flush()  # populate match.id without committing yet

        output.append(
            schemas.MatchResultOut(
                id=match.id,
                job_id=job.id,
                resume_id=resume.id,
                candidate_name=resume.candidate_name,
                file_name=resume.file_name,
                overall_score=result["overall_score"],
                semantic_score=result["semantic_score"],
                skill_score=result["skill_score"],
                experience_score=result["experience_score"],
                matched_skills=result["matched_skills"],
                missing_skills=result["missing_skills"],
                explanation=result["explanation"],
                rank=idx,
            )
        )

    db.commit()

    return schemas.ScreeningResponse(
        job_id=job.id,
        job_title=job.title,
        total_candidates=len(output),
        results=output,
    )


@router.get("/results/{job_id}", response_model=schemas.ScreeningResponse)
def get_screening_results(job_id: int, db: Session = Depends(get_db)):
    """Fetch the most recently computed ranking for a given job."""
    job = db.query(db_models.JobDescription).filter(db_models.JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")

    matches = (
        db.query(db_models.MatchResult)
        .filter(db_models.MatchResult.job_id == job_id)
        .order_by(db_models.MatchResult.rank.asc())
        .all()
    )

    output = []
    for match in matches:
        resume = db.query(db_models.Resume).filter(db_models.Resume.id == match.resume_id).first()
        output.append(
            schemas.MatchResultOut(
                id=match.id,
                job_id=match.job_id,
                resume_id=match.resume_id,
                candidate_name=resume.candidate_name if resume else None,
                file_name=resume.file_name if resume else None,
                overall_score=match.overall_score,
                semantic_score=match.semantic_score,
                skill_score=match.skill_score,
                experience_score=match.experience_score,
                matched_skills=match.matched_skills,
                missing_skills=match.missing_skills,
                explanation=match.explanation,
                rank=match.rank,
            )
        )

    return schemas.ScreeningResponse(
        job_id=job.id,
        job_title=job.title,
        total_candidates=len(output),
        results=output,
    )
