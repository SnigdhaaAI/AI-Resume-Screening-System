import React, { useEffect, useRef, useState } from "react";
import { deleteResume, listResumes, uploadResumesBatch } from "../api/client";

export default function ResumesPage() {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  async function refresh() {
    setLoading(true);
    try {
      setResumes(await listResumes());
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

  async function handleFiles(fileList) {
    const files = Array.from(fileList);
    if (files.length === 0) return;
    setUploading(true);
    setError(null);
    try {
      const result = await uploadResumesBatch(files);
      if (Array.isArray(result) && result.length < files.length) {
        setError(`${files.length - result.length} file(s) failed to process. Check formats (.pdf, .docx, .doc, .txt).`);
      }
      await refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(id) {
    try {
      await deleteResume(id);
      await refresh();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div>
      <div className="page-header">
        <div className="eyebrow">02 — Candidates</div>
        <h1 className="page-title">Resumes</h1>
        <p className="page-desc">
          Upload candidate resumes (.pdf, .docx, .doc, .txt). Each one is parsed
          for contact details, skills, and years of experience, then embedded
          for semantic matching.
        </p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="panel">
        <h2 className="panel-title">Upload resumes</h2>
        <div
          className="dropzone"
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            handleFiles(e.dataTransfer.files);
          }}
          style={dragOver ? { borderColor: "var(--accent)", color: "var(--text)" } : undefined}
        >
          {uploading ? (
            <>
              <span className="spinner" /> Uploading and processing…
            </>
          ) : (
            <>Drop resume files here, or click to browse</>
          )}
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.docx,.doc,.txt"
            style={{ display: "none" }}
            onChange={(e) => handleFiles(e.target.files)}
          />
        </div>
      </div>

      <div className="panel">
        <h2 className="panel-title">All candidates</h2>
        {loading ? (
          <div className="empty-state">
            <span className="spinner" /> Loading resumes…
          </div>
        ) : resumes.length === 0 ? (
          <div className="empty-state">No resumes uploaded yet.</div>
        ) : (
          <div className="list">
            {resumes.map((r) => (
              <div className="list-item" key={r.id}>
                <div>
                  <p className="item-title">{r.candidate_name || r.file_name}</p>
                  <p className="item-sub">
                    {r.email ? `${r.email} · ` : ""}
                    {r.experience_years != null ? `${r.experience_years} yrs · ` : ""}
                    Resume #{r.id} · added {new Date(r.created_at).toLocaleDateString()}
                  </p>
                  {r.extracted_skills?.length > 0 && (
                    <div style={{ marginTop: 8 }}>
                      {r.extracted_skills.slice(0, 8).map((s) => (
                        <span className="tag" key={s}>
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <button className="btn btn-danger" onClick={() => handleDelete(r.id)}>
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
