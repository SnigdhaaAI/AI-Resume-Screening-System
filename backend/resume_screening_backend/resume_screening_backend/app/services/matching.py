"""
Computes match scores between a job description and a resume, combining:
  1. Semantic similarity (transformer embeddings, cosine similarity)
  2. Skill overlap (explicit taxonomy matching)
  3. Experience fit (years required vs. years held)

Also produces a human-readable explanation for each score, satisfying the
"explainable insights" requirement.
"""
from typing import List, Optional, Tuple, Dict

import numpy as np

from app.config import settings


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    a = np.asarray(vec_a, dtype=np.float32)
    b = np.asarray(vec_b, dtype=np.float32)
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    sim = float(np.dot(a, b) / denom)
    # Clamp for numerical safety, then map [-1, 1] -> [0, 1]
    sim = max(-1.0, min(1.0, sim))
    return (sim + 1) / 2


def compute_skill_score(job_skills: List[str], resume_skills: List[str]) -> Tuple[float, List[str], List[str]]:
    job_set = set(job_skills or [])
    resume_set = set(resume_skills or [])

    if not job_set:
        # No explicit skills parsed from the JD -> skill dimension is neutral
        return 1.0, sorted(resume_set), []

    matched = sorted(job_set & resume_set)
    missing = sorted(job_set - resume_set)
    score = len(matched) / len(job_set)
    return score, matched, missing


def compute_experience_score(required_years: Optional[float], candidate_years: Optional[float]) -> float:
    if not required_years or required_years <= 0:
        return 1.0  # No requirement specified -> neutral/full score
    if candidate_years is None:
        return 0.4  # Unknown experience -> mild penalty, not disqualifying
    if candidate_years >= required_years:
        return 1.0
    # Partial credit, scaled linearly, floor at 0
    return max(0.0, candidate_years / required_years)


def build_explanation(
    semantic_score: float,
    skill_score: float,
    experience_score: float,
    matched_skills: List[str],
    missing_skills: List[str],
    required_years: Optional[float],
    candidate_years: Optional[float],
) -> str:
    parts = []

    parts.append(f"Semantic similarity to job description: {semantic_score * 100:.1f}%.")

    if matched_skills:
        parts.append(f"Matched {len(matched_skills)} required skill(s): {', '.join(matched_skills)}.")
    else:
        parts.append("No required skills were matched.")

    if missing_skills:
        parts.append(f"Missing {len(missing_skills)} required skill(s): {', '.join(missing_skills)}.")

    if required_years:
        if candidate_years is None:
            parts.append(
                f"Job requires {required_years:g}+ years of experience; "
                "candidate's experience could not be determined from the resume."
            )
        elif candidate_years >= required_years:
            parts.append(
                f"Candidate has {candidate_years:g} years of experience, meeting the "
                f"{required_years:g}-year requirement."
            )
        else:
            parts.append(
                f"Candidate has {candidate_years:g} years of experience, below the "
                f"{required_years:g}-year requirement."
            )

    return " ".join(parts)


def compute_match(
    job_embedding: List[float],
    resume_embedding: List[float],
    job_skills: List[str],
    resume_skills: List[str],
    required_years: Optional[float],
    candidate_years: Optional[float],
) -> Dict:
    """Compute the full weighted match result between one job and one resume."""
    semantic_score = cosine_similarity(job_embedding, resume_embedding)
    skill_score, matched_skills, missing_skills = compute_skill_score(job_skills, resume_skills)
    experience_score = compute_experience_score(required_years, candidate_years)

    overall = (
        semantic_score * settings.SEMANTIC_WEIGHT
        + skill_score * settings.SKILL_WEIGHT
        + experience_score * settings.EXPERIENCE_WEIGHT
    )

    explanation = build_explanation(
        semantic_score, skill_score, experience_score,
        matched_skills, missing_skills, required_years, candidate_years,
    )

    return {
        "overall_score": round(overall * 100, 2),
        "semantic_score": round(semantic_score * 100, 2),
        "skill_score": round(skill_score * 100, 2),
        "experience_score": round(experience_score * 100, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "explanation": explanation,
    }
