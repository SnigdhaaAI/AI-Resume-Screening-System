import React from "react";

const NAV_ITEMS = [
  { key: "jobs", label: "Jobs", index: "01" },
  { key: "resumes", label: "Resumes", index: "02" },
  { key: "screening", label: "Screening", index: "03" },
];

export default function Sidebar({ page, onNavigate, apiOnline }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark" />
        <div>
          <div className="brand-name">Signal</div>
          <div className="brand-sub">Resume Screening</div>
        </div>
      </div>

      <nav className="nav">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.key}
            className={`nav-item${page === item.key ? " active" : ""}`}
            onClick={() => onNavigate(item.key)}
          >
            <span className="nav-index">{item.index}</span>
            {item.label}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <span className={`status-dot${apiOnline ? " online" : ""}`} />
        {apiOnline ? "API connected" : "API unreachable"}
      </div>
    </aside>
  );
}
