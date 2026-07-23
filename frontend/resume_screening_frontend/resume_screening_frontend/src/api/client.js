// Thin client for the resume-screening FastAPI backend.
// All routes are mounted under settings.API_V1_PREFIX ("/api/v1") in app/main.py.

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const API = `${BASE_URL}/api/v1`;

async function handle(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ? JSON.stringify(body.detail) : detail;
    } catch (_) {
      /* no json body */
    }
    throw new Error(detail || `Request failed (${res.status})`);
  }
  if (res.status === 204) return null;
  return res.json();
}

// ---------- Health ----------
export function getHealth() {
  return fetch(`${BASE_URL}/health`).then(handle);
}

// ---------- Jobs ----------
export function listJobs() {
  return fetch(`${API}/jobs/`).then(handle);
}

export function getJob(jobId) {
  return fetch(`${API}/jobs/${jobId}`).then(handle);
}

export function createJob({ title, company, raw_text, min_experience_years }) {
  return fetch(`${API}/jobs/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, company, raw_text, min_experience_years }),
  }).then(handle);
}

export function deleteJob(jobId) {
  return fetch(`${API}/jobs/${jobId}`, { method: "DELETE" }).then(handle);
}

// ---------- Resumes ----------
export function listResumes() {
  return fetch(`${API}/resumes/`).then(handle);
}

export function getResume(resumeId) {
  return fetch(`${API}/resumes/${resumeId}`).then(handle);
}

export function uploadResume(file) {
  const form = new FormData();
  form.append("file", file);
  return fetch(`${API}/resumes/upload`, { method: "POST", body: form }).then(handle);
}

export function uploadResumesBatch(files) {
  const form = new FormData();
  files.forEach((file) => form.append("files", file));
  return fetch(`${API}/resumes/upload-batch`, { method: "POST", body: form }).then(handle);
}

export function deleteResume(resumeId) {
  return fetch(`${API}/resumes/${resumeId}`, { method: "DELETE" }).then(handle);
}

// ---------- Screening ----------
export function runScreening({ job_id, resume_ids, top_k }) {
  return fetch(`${API}/screening/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_id, resume_ids, top_k }),
  }).then(handle);
}

export function getScreeningResults(jobId) {
  return fetch(`${API}/screening/results/${jobId}`).then(handle);
}
