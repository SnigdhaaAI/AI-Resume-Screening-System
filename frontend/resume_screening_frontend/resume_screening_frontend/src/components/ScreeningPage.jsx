import React, { useEffect, useState } from "react";
import { listJobs, listResumes, runScreening, getScreeningResults } from "../api/client";
import ScoreDial from "./ScoreDial";

export default function ScreeningPage() {
  const [jobs, setJobs] = useState([]);
  const [resumes, setResumes] = useState([]);
  const [jobId, setJobId] = useState("");
  const [selectedResumeIds, setSelectedResumeIds] = useState(new Set());
  const [topK, setTopK] = useState("");
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const [j, r] = await Promise.all([listJobs(), listResumes()]);
        setJobs(j);
        setResumes(r);
        if (j.length > 0) setJobId(String(j[0].id));
      } catch (e) {
        setError(e.message);
      }
    })();
  }, []);

  function toggleResume(id) {
    setSelectedResumeIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function toggleAll() {
    setSelectedResumeIds((prev) =>
      prev.size === resumes.length ? new Set() : new Set(resumes.map((r) => r.id))
    );
  }

  async function handleRun() {
    if (!jobId) {
      setError("Choose a job description first.");
      return;
    }
    setRunning(true);
    setError(null);
    try {
      const payload = {
        job_id: Number(jobId),
        resume_ids: selectedResumeIds.size > 0 ? Array.from(selectedResumeIds) : undefined,
        top_k: topK ? Number(topK) : undefined,
      };
      const data = await runScreening(payload);
      setResults(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setRunning(false);
    }
  }

  async function handleLoadPrevious() {
    if (!jobId) return;
    setRunning(true);
    setError(null);
    try {
      const data = await getScreeningResults(Number(jobId));
      setResults(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setRunning(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <div className="eyebrow">03 — Ranking</div>
        <h1 className="page-title">Run screening</h1>
        <p className="page-desc">
          Pick a job and, optionally, a specific set of candidates. The backend
          scores each resume on semantic fit, skill overlap, and experience,
          then returns a ranked, explainable shortlist.
        </p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="panel">
        <h2 className="panel-title">Configure run</h2>
        <div className="field-row">
          <div className="field">
            <label>Job description</label>
            <select
              value={jobId}
              onChange={(e) => setJobId(e.target.value)}
              style={{
                background: "var(--bg)",
                border: "1px solid var(--border)",
                borderRadius: 6,
                padding: "10px 12px",
                color: "var(--text)",
                fontFamily: "var(--font-body)",
                fontSize: 14,
              }}
            >
              <option value="" disabled>
                Select a job…
              </option>
              {jobs.map((j) => (
                <option value={j.id} key={j.id}>
                  {j.title}
                  {j.company ? ` · ${j.company}` : ""}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Top K (optional)</label>
            <input
              type="number"
              min="1"
              value={topK}
              onChange={(e) => setTopK(e.target.value)}
              placeholder="All candidates"
            />
          </div>
        </div>

        <div className="field">
          <label>
            Candidates ({selectedResumeIds.size > 0 ? selectedResumeIds.size : "all"} selected)
          </label>
          {resumes.length === 0 ? (
            <p className="item-sub">No resumes uploaded yet — upload some on the Resumes page.</p>
          ) : (
            <>
              <div className="checkbox-row select-all">
                <input
                  type="checkbox"
                  checked={selectedResumeIds.size === resumes.length}
                  onChange={toggleAll}
                />
                Select all (leave unchecked to screen every candidate)
              </div>
              <div className="list">
                {resumes.map((r) => (
                  <div
                    className={`list-item selectable${
                      selectedResumeIds.has(r.id) ? " selected" : ""
                    }`}
                    key={r.id}
                    onClick={() => toggleResume(r.id)}
                  >
                    <div>
                      <p className="item-title">{r.candidate_name || r.file_name}</p>
                      <p className="item-sub">Resume #{r.id}</p>
                    </div>
                    <input type="checkbox" checked={selectedResumeIds.has(r.id)} readOnly />
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        <div className="btn-row">
          <button className="btn" onClick={handleRun} disabled={running || !jobId}>
            {running ? "Running…" : "Run screening"}
          </button>
          <button className="btn btn-ghost" onClick={handleLoadPrevious} disabled={running || !jobId}>
            Load previous results
          </button>
        </div>
      </div>

      {results && (
        <div className="panel">
          <h2 className="panel-title">
            Results for “{results.job_title}” · {results.total_candidates} candidate
            {results.total_candidates === 1 ? "" : "s"}
          </h2>
          {results.results.length === 0 ? (
            <div className="empty-state">No matches to show.</div>
          ) : (
            results.results.map((m) => (
              <div className="result-card" key={m.id}>
                <div className="result-rank">{String(m.rank).padStart(2, "0")}</div>
                <ScoreDial score={m.overall_score} />
                <div className="result-body">
                  <div className="result-header">
                    <span className="result-name">{m.candidate_name || "Unnamed candidate"}</span>
                    <span className="result-file">{m.file_name}</span>
                  </div>
                  {m.explanation && <p className="result-explanation">{m.explanation}</p>}
                  <div>
                    {m.matched_skills?.map((s) => (
                      <span className="tag matched" key={`m-${s}`}>
                        {s}
                      </span>
                    ))}
                    {m.missing_skills?.map((s) => (
                      <span className="tag missing" key={`x-${s}`}>
                        {s}
                      </span>
                    ))}
                  </div>
                  <div className="sub-scores">
                    <span>
                      Semantic <b>{Math.round(m.semantic_score * 100)}</b>
                    </span>
                    <span>
                      Skills <b>{Math.round(m.skill_score * 100)}</b>
                    </span>
                    <span>
                      Experience <b>{Math.round(m.experience_score * 100)}</b>
                    </span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
