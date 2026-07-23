# AI-Based Resume Screening System — Backend

A FastAPI backend that screens resumes against job descriptions using NLP
preprocessing, transformer embeddings, and similarity-based ranking with
explainable score breakdowns.

## Pipeline

1. **Ingest** — job descriptions (raw text) and resumes (`.pdf`, `.docx`, `.doc`, `.txt` upload)
2. **Extract & preprocess** — text extraction (pdfplumber / python-docx), cleaning, skill/email/phone/experience extraction
3. **Embed** — `sentence-transformers/all-MiniLM-L6-v2` generates dense vector embeddings
4. **Match** — cosine similarity (semantic) + skill overlap + experience fit, combined into a weighted overall score
5. **Rank & explain** — candidates sorted by score; each result includes matched/missing skills and a plain-language explanation

## Project structure

```
resume_screening_backend/
├── app/
│   ├── main.py                # FastAPI app + router registration
│   ├── config.py               # settings (weights, paths, model name)
│   ├── database.py             # SQLAlchemy engine/session
│   ├── models/
│   │   ├── db_models.py        # ORM tables: JobDescription, Resume, MatchResult
│   │   └── schemas.py          # Pydantic request/response models
│   ├── services/
│   │   ├── text_extraction.py  # PDF/DOCX/TXT -> raw text
│   │   ├── preprocessing.py    # cleaning + skill/email/phone/experience extraction
│   │   ├── embeddings.py       # sentence-transformers embedding generation
│   │   └── matching.py         # similarity scoring + explanations
│   └── routers/
│       ├── jobs.py             # /api/v1/jobs
│       ├── resumes.py          # /api/v1/resumes
│       └── screening.py        # /api/v1/screening
├── uploads/                    # uploaded resume files (gitignored)
├── requirements.txt
├── run.py
└── .env.example
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # optional, defaults work out of the box
```

> **Note:** The first request that generates an embedding will download the
> `all-MiniLM-L6-v2` model (~90MB) from Hugging Face. Make sure the machine
> has internet access on first run, or pre-download the model.

## Run

```bash
python run.py
# or
uvicorn app.main:app --reload
```

- API base: `http://localhost:8000/api/v1`
- Interactive docs (Swagger): `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API overview

### Job descriptions
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/jobs/` | Create a job description (raw text is parsed, embedded, and stored) |
| GET | `/api/v1/jobs/` | List all job descriptions |
| GET | `/api/v1/jobs/{id}` | Get one job description |
| DELETE | `/api/v1/jobs/{id}` | Delete a job description |

**Example — create a job:**
```bash
curl -X POST http://localhost:8000/api/v1/jobs/ \
  -H "Content-Type: application/json" \
  -d '{
        "title": "Backend Engineer",
        "company": "Acme Corp",
        "raw_text": "We are looking for a Backend Engineer with 3+ years of experience in Python, FastAPI, PostgreSQL, and Docker. Experience with AWS and CI/CD pipelines is a plus.",
        "min_experience_years": 3
      }'
```

### Resumes
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/resumes/upload` | Upload a single resume file |
| POST | `/api/v1/resumes/upload-batch` | Upload multiple resume files |
| GET | `/api/v1/resumes/` | List all resumes |
| GET | `/api/v1/resumes/{id}` | Get one resume |
| DELETE | `/api/v1/resumes/{id}` | Delete a resume |

**Example — upload a resume:**
```bash
curl -X POST http://localhost:8000/api/v1/resumes/upload \
  -F "file=@/path/to/resume.pdf"
```

### Screening & ranking
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/screening/run` | Score + rank resumes against a job description |
| GET | `/api/v1/screening/results/{job_id}` | Fetch the last computed ranking for a job |

**Example — run screening:**
```bash
curl -X POST http://localhost:8000/api/v1/screening/run \
  -H "Content-Type: application/json" \
  -d '{"job_id": 1, "top_k": 10}'
```

**Example response:**
```json
{
  "job_id": 1,
  "job_title": "Backend Engineer",
  "total_candidates": 2,
  "results": [
    {
      "id": 5,
      "job_id": 1,
      "resume_id": 3,
      "candidate_name": "Jane Doe",
      "file_name": "jane_doe_resume.pdf",
      "overall_score": 87.4,
      "semantic_score": 82.1,
      "skill_score": 100.0,
      "experience_score": 100.0,
      "matched_skills": ["python", "fastapi", "postgresql", "docker"],
      "missing_skills": [],
      "explanation": "Semantic similarity to job description: 82.1%. Matched 4 required skill(s): python, fastapi, postgresql, docker. Candidate has 5 years of experience, meeting the 3-year requirement.",
      "rank": 1
    }
  ]
}
```

## Scoring methodology

The overall score is a weighted combination (configurable in `app/config.py`):

- **Semantic similarity (60%)** — cosine similarity between job and resume embeddings
- **Skill overlap (30%)** — fraction of the job's required skills found in the resume
- **Experience fit (10%)** — candidate years vs. minimum years required

Each dimension, plus matched/missing skills, is returned so results are
explainable rather than a black-box score.

## Extending

- **Skills taxonomy** — expand `SKILLS_TAXONOMY` in `app/services/preprocessing.py`, or swap in an external taxonomy (ESCO, O*NET, LinkedIn Skills API).
- **Better name/entity extraction** — swap the regex heuristics in `preprocessing.py` for a spaCy NER pipeline if higher accuracy is needed.
- **Different embedding model** — change `EMBEDDING_MODEL_NAME` in `.env` (e.g. a larger `all-mpnet-base-v2` for higher quality at more compute cost).
- **Vector DB** — for large-scale deployments, replace the JSON-column embedding storage with a vector database (pgvector, Pinecone, Qdrant, etc.) for faster similarity search.
- **Auth** — add API key / OAuth2 middleware before exposing publicly; CORS is wide open by default for local development.
