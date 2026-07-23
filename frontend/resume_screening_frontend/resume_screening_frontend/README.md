# Signal — Resume Screening Frontend

A React (Vite) frontend for the `resume_screening_backend` FastAPI project.
It covers the three things the backend exposes:

- **Jobs** — create and browse job descriptions (`/api/v1/jobs`)
- **Resumes** — upload and browse candidate resumes (`/api/v1/resumes`)
- **Screening** — run matching/ranking and view scored results (`/api/v1/screening`)

## 1. Start the backend first

From the `resume_screening_backend` folder:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

This serves the API at `http://localhost:8000` (CORS is already open on the
backend, `allow_origins=["*"]`, so no backend changes are needed).

## 2. Configure and run the frontend

```bash
cd resume_screening_frontend
cp .env.example .env       # defaults to http://localhost:8000
npm install
npm run dev
```

Open the printed local URL (default `http://localhost:5173`).

If your backend runs somewhere other than `http://localhost:8000`, edit
`VITE_API_URL` in `.env`.

## 3. Build for production

```bash
npm run build
npm run preview   # serve the built files locally to sanity-check
```

The build output lands in `dist/`, ready to deploy behind any static host —
just make sure `VITE_API_URL` points at wherever the FastAPI backend is
actually reachable at build time.

## How it talks to the backend

All requests go through `src/api/client.js`, a thin wrapper around `fetch`
that mirrors the backend's routes exactly:

| Function                | Method & path                          |
|-------------------------|-----------------------------------------|
| `listJobs()`             | `GET /api/v1/jobs/`                    |
| `createJob(data)`        | `POST /api/v1/jobs/`                   |
| `deleteJob(id)`          | `DELETE /api/v1/jobs/{id}`             |
| `listResumes()`          | `GET /api/v1/resumes/`                 |
| `uploadResumesBatch()`   | `POST /api/v1/resumes/upload-batch`    |
| `deleteResume(id)`       | `DELETE /api/v1/resumes/{id}`          |
| `runScreening(payload)`  | `POST /api/v1/screening/run`           |
| `getScreeningResults(id)`| `GET /api/v1/screening/results/{id}`   |

The sidebar shows a live "API connected" indicator backed by the backend's
`/health` endpoint, polled every 15 seconds.

## Design notes

The visual language ("Signal") treats each match score as a radial dial —
an arc sweep colored by strength (teal = strong, amber = medium, rust =
weak) — echoing the idea of tuning in a signal from noise across a pile of
resumes. Headings use Space Grotesk, body text uses Inter, and scores/IDs
use IBM Plex Mono to read as data rather than prose.
