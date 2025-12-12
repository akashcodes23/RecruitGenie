"use client";
import { useEffect, useState } from "react";

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<any>(null);
  const API = "http://127.0.0.1:8001";

  async function load(jobId?: string) {
    const q = jobId ? `?job_id=${encodeURIComponent(jobId)}` : "";
    const res = await fetch(`${API}/analytics/summary${q}`);
    const json = await res.json();
    setSummary(json);
  }

  useEffect(() => { load(); }, []);

  if (!summary) return <main style={{ padding: 20 }}><p>Loading...</p></main>;

  return (
    <main style={{ padding: 20 }}>
      <h2>Analytics</h2>
      <p>Total candidates: {summary.total}</p>
      <p>Average score: {summary.avg_score}</p>
      <div>
        <h4>Status counts</h4>
        <pre>{JSON.stringify(summary.status_counts, null, 2)}</pre>
      </div>
      <div>
        <h4>Top missing skills</h4>
        <ul>
          {(summary.top_missing_skills || []).map((s:any) => <li key={s.skill}>{s.skill} — {s.count}</li>)}
        </ul>
      </div>
    </main>
  );
}