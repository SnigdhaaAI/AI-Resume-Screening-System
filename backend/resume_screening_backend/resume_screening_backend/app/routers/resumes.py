"""
Endpoints for uploading and managing candidate resumes.
"""
import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import db_models, schemas
from app.services import text_extraction, preprocessing, embeddings

router = APIRouter(prefix="/resumes", tags=["Resumes"])


def _validate_upload(file: UploadFile):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {sorted(settings.ALLOWED_EXTENSIONS)}",
        )


def _save_upload(file: UploadFile) -> str:
    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    dest_path = os.path.join(settings.RESUME_DIR, unique_name)
    with open(dest_path, "wb") as out:
        content = file.file.read()
        if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large")
        out.write(content)
    return dest_path


def _process_and_store_resume(file_path: str, original_name: str, db: Session) -> db_models.Resume:
    raw_text = text_extraction.extract_text(file_path)
    processed = preprocessing.preprocess_document(raw_text)
    candidate_name = preprocessing.extract_candidate_name(raw_text)
    vector = embeddings.generate_embedding(processed["cleaned_text"])

    resume = db_models.Resume(
        candidate_name=candidate_name,
        file_name=original_name,
        file_path=file_path,
        raw_text=raw_text,
        cleaned_text=processed["cleaned_text"],
        extracted_skills=processed["skills"],
        experience_years=processed["experience_years"],
        email=processed["email"],
        phone=processed["phone"],
        embedding=vector,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.post("/upload", response_model=schemas.ResumeOut, status_code=201)
def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a single resume file (.pdf, .docx, .doc, .txt)."""
    _validate_upload(file)
    file_path = _save_upload(file)
    try:
        resume = _process_and_store_resume(file_path, file.filename, db)
    except Exception:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    return resume


@router.post("/upload-batch", response_model=List[schemas.ResumeOut], status_code=201)
def upload_resumes_batch(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    """Upload multiple resumes at once."""
    results = []
    errors = []
    for file in files:
        try:
            _validate_upload(file)
            file_path = _save_upload(file)
            resume = _process_and_store_resume(file_path, file.filename, db)
            results.append(resume)
        except HTTPException as exc:
            errors.append({"file": file.filename, "error": exc.detail})
        except Exception as exc:
            errors.append({"file": file.filename, "error": str(exc)})

    if not results and errors:
        raise HTTPException(status_code=422, detail={"message": "All uploads failed", "errors": errors})

    return results


@router.get("/", response_model=List[schemas.ResumeOut])
def list_resumes(db: Session = Depends(get_db)):
    return db.query(db_models.Resume).order_by(db_models.Resume.created_at.desc()).all()


@router.get("/{resume_id}", response_model=schemas.ResumeOut)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(db_models.Resume).filter(db_models.Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.delete("/{resume_id}", status_code=204)
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(db_models.Resume).filter(db_models.Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.file_path and os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    db.delete(resume)
    db.commit()
    return None
