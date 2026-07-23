import React, { useEffect, useState } from "react";
import { createJob, deleteJob, listJobs } from "../api/client";

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const [title, setTitle] = useState("");
  const [company, setCompany] = useState("");
  const [rawText, setRawText] = useState("");
  const [minYears, setMinYears] = useState("");

  async function refresh() {
    setLoading(true);
    try {
      setJobs(await listJobs());
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!title.trim() || rawText.trim().length < 20) {
      setError("Title is required and the description needs at least 20 characters.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await createJob({
        title: title.trim(),
        company: company.trim() || undefined,
        raw_text: rawText.trim(),
        min_experience_years: minYears ? Number(minYears) : undefined,
      });
      setTitle("");
      setCompany("");
      setRawText("");
      setMinYears("");
      await refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(id) {
    try {
      await deleteJob(id);
      await refresh();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div>
      <div className="page-header">
        <div className="eyebrow">01 — Postings</div>
        <h1 className="page-title">Job descriptions</h1>
        <p className="page-desc">
          Add a role. The backend cleans the text, pulls out required skills and
          experience, and generates an embedding used later for matching.
        </p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="panel">
        <h2 className="panel-title">New job description</h2>
        <form onSubmit={handleSubmit}>
          <div className="field-row">
            <div className="field">
              <label>Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Senior Backend Engineer"
              />
            </div>
            <div className="field">
              <label>Company (optional)</label>
              <input
                type="text"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                placeholder="Acme Corp"
              />
            </div>
          </div>
          <div className="field">
            <label>Description</label>
            <textarea
              rows={6}
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              placeholder="Paste the full job description here..."
            />
          </div>
          <div className="field" style={{ maxWidth: 220 }}>
            <label>Minimum years experience (optional)</label>
            <input
              type="number"
              min="0"
              step="0.5"
              value={minYears}
              onChange={(e) => setMinYears(e.target.value)}
              placeholder="Auto-detected if left blank"
            />
          </div>
          <button className="btn" type="submit" disabled={submitting}>
            {submitting ? "Creating…" : "Create job"}
          </button>
        </form>
      </div>

      <div className="panel">
        <h2 className="panel-title">All jobs</h2>
        {loading ? (
          <div className="empty-state">
            <span className="spinner" /> Loading jobs…
          </div>
        ) : jobs.length === 0 ? (
          <div className="empty-state">No jobs yet. Create one above to get started.</div>
        ) : (
          <div className="list">
            {jobs.map((job) => (
              <div className="list-item" key={job.id}>
                <div>
                  <p className="item-title">
                    {job.title}
                    {job.company ? ` · ${job.company}` : ""}
                  </p>
                  <p className="item-sub">
                    {job.min_experience_years != null
                      ? `${job.min_experience_years}+ yrs experience · `
                      : ""}
                    Job #{job.id} · added {new Date(job.created_at).toLocaleDateString()}
                  </p>
                  {job.required_skills?.length > 0 && (
                    <div style={{ marginTop: 8 }}>
                      {job.required_skills.slice(0, 8).map((s) => (
                        <span className="tag" key={s}>
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <button className="btn btn-danger" onClick={() => handleDelete(job.id)}>
                  Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
