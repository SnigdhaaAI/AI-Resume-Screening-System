"""
Application configuration.
Values can be overridden via environment variables or a .env file.
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AI Resume Screening System"
    API_V1_PREFIX: str = "/api/v1"

    # Storage
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    RESUME_DIR: str = os.path.join(UPLOAD_DIR, "resumes")
    JOB_DIR: str = os.path.join(UPLOAD_DIR, "job_descriptions")

    # Database
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'resume_screening.db')}"

    # Embedding model (downloaded from HuggingFace on first run)
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Matching weights (must sum to 1.0)
    SEMANTIC_WEIGHT: float = 0.6
    SKILL_WEIGHT: float = 0.3
    EXPERIENCE_WEIGHT: float = 0.1

    # Upload limits
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx", ".doc", ".txt"}

    class Config:
        env_file = ".env"


settings = Settings()

# Ensure storage directories exist at import time
os.makedirs(settings.RESUME_DIR, exist_ok=True)
os.makedirs(settings.JOB_DIR, exist_ok=True)
