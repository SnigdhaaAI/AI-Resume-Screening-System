import React, { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar";
import JobsPage from "./components/JobsPage";
import ResumesPage from "./components/ResumesPage";
import ScreeningPage from "./components/ScreeningPage";
import { getHealth } from "./api/client";

export default function App() {
  const [page, setPage] = useState("jobs");
  const [apiOnline, setApiOnline] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function check() {
      try {
        await getHealth();
        if (!cancelled) setApiOnline(true);
      } catch {
        if (!cancelled) setApiOnline(false);
      }
    }
    check();
    const interval = setInterval(check, 15000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="app-shell">
      <Sidebar page={page} onNavigate={setPage} apiOnline={apiOnline} />
      <main className="main">
        {page === "jobs" && <JobsPage />}
        {page === "resumes" && <ResumesPage />}
        {page === "screening" && <ScreeningPage />}
      </main>
    </div>
  );
}
