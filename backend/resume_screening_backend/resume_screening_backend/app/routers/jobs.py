"""
Endpoints for creating and managing job descriptions.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import db_models, schemas
from app.services import preprocessing, embeddings

router = APIRouter(prefix="/jobs", tags=["Job Descriptions"])


@router.post("/", response_model=schemas.JobDescriptionOut, status_code=201)
def create_job(payload: schemas.JobDescriptionCreate, db: Session = Depends(get_db)):
    """Create a job description from raw text, run NLP preprocessing, and embed it."""
    processed = preprocessing.preprocess_document(payload.raw_text)
    vector = embeddings.generate_embedding(processed["cleaned_text"])

    job = db_models.JobDescription(
        title=payload.title,
        company=payload.company,
        raw_text=payload.raw_text,
        cleaned_text=processed["cleaned_text"],
        required_skills=processed["skills"],
        min_experience_years=payload.min_experience_years or processed["experience_years"],
        embedding=vector,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/", response_model=List[schemas.JobDescriptionOut])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(db_models.JobDescription).order_by(db_models.JobDescription.created_at.desc()).all()


@router.get("/{job_id}", response_model=schemas.JobDescriptionOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(db_models.JobDescription).filter(db_models.JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    return job


@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(db_models.JobDescription).filter(db_models.JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    db.delete(job)
    db.commit()
    return None
