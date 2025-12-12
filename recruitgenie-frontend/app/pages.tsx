// recruitgenie-frontend/src/app/candidates/page.tsx
"use client";

import React, { useEffect, useState } from "react";

type Candidate = {
  _id?: number;
  job_id?: string;
  name?: string;
  email?: string;
  phone?: string;
  total_score?: string | number;
  base_score?: string | number;
  skill_score?: string | number;
  penalty?: string | number;
  questions?: string;
  missing_skills?: string;
  status?: string;
  notes?: string;
};

const API_BASE = "http://localhost:8001";

export default function CandidatesPage() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pageSize] = useState(50);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);

  async function loadCandidates() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/candidates?limit=${pageSize}&offset=${offset}`);
      if (!res.ok) throw new Error(`Failed to load: ${res.status}`);
      const json = await res.json();
      setCandidates(json.candidates || []);
      setTotal(json.total || 0);
    } catch (err: any) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCandidates();
  }, [offset]);

  async function setStatus(id: number, status: string) {
    try {
      const res = await fetch(`${API_BASE}/candidates/${id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
      });
      if (!res.ok) throw new Error(`update failed ${res.status}`);
      // refresh
      await loadCandidates();
    } catch (e: any) {
      alert("Failed to update status: " + (e.message || e));
    }
  }

  function nextPage() {
    if (offset + pageSize < total) setOffset(offset + pageSize);
  }
  function prevPage() {
    if (offset - pageSize >= 0) setOffset(Math.max(0, offset - pageSize));
  }

  return (
    <main style={{ padding: 24, fontFamily: "Inter, system-ui, sans-serif" }}>
      <h1>Candidates</h1>

      <div style={{ marginBottom: 12 }}>
        <button onClick={prevPage} disabled={offset === 0} style={{ marginRight: 8 }}>
          ◀ Prev
        </button>
        <button onClick={nextPage} disabled={offset + pageSize >= total}>
          Next ▶
        </button>
        <span style={{ marginLeft: 12 }}>
          Showing {Math.min(offset + 1, total)}–{Math.min(offset + pageSize, total)} of {total}
        </span>
      </div>

      {loading && <p>Loading…</p>}
      {error && <p style={{ color: "crimson" }}>Error: {error}</p>}

      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 1000 }}>
          <thead>
            <tr>
              <th style={th}>#</th>
              <th style={th}>Job</th>
              <th style={th}>Name</th>
              <th style={th}>Email</th>
              <th style={th}>Total</th>
              <th style={th}>Missing Skills</th>
              <th style={th}>Status</th>
              <th style={th}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {candidates.map((c, i) => (
              <tr key={c._id ?? i} style={i % 2 ? rowAlt : undefined}>
                <td style={td}>{c._id ?? i + 1}</td>
                <td style={td}>{c.job_id}</td>
                <td style={td}>{c.name}</td>
                <td style={td}>{c.email}</td>
                <td style={td}>{c.total_score}</td>
                <td style={td}>
                  {String(c.missing_skills || c["missing_skills"] || "")
                    .replace(/\|/g, ",")
                    .slice(0, 120)}
                </td>
                <td style={td}>{c.status || "unknown"}</td>
                <td style={td}>
                  <button onClick={() => setStatus(c._id ?? i + 1, "shortlisted")} style={{ marginRight: 6 }}>
                    Shortlist
                  </button>
                  <button onClick={() => setStatus(c._id ?? i + 1, "reject")} style={{ marginRight: 6 }}>
                    Reject
                  </button>
                  <button onClick={() => setStatus(c._id ?? i + 1, "review")}>Review</button>
                </td>
              </tr>
            ))}
            {candidates.length === 0 && !loading && (
              <tr>
                <td style={td} colSpan={8}>
                  No candidates yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </main>
  );
}

const th: React.CSSProperties = {
  textAlign: "left",
  padding: "8px 10px",
  borderBottom: "1px solid #e6e6e6",
  background: "#fafafa",
  fontWeight: 600,
};

const td: React.CSSProperties = {
  padding: "8px 10px",
  borderBottom: "1px solid #f2f2f2",
};

const rowAlt: React.CSSProperties = {
  background: "#fbfbfb",
};
