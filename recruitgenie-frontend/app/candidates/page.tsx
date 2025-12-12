// recruitgenie-frontend/app/candidates/page.tsx
"use client";

import React, { useEffect, useState } from "react";

type Candidate = {
  _id?: number;
  job_id?: string;
  name?: string;
  email?: string;
  phone?: string;
  total_score?: number | string;
  base_score?: number | string;
  skill_score?: number | string;
  penalty?: number | string;
  missing_skills?: string;
  questions?: string | string[];
  status?: string;
  notes?: string;
};

// read from environment (next): allows easy switching between dev/staging
const API_BASE = (process.env.NEXT_PUBLIC_API_BASE as string) || "http://localhost:8001";

/**
 * ErrorBoundary (client) — included here so you don't need to create a separate file.
 * It will render the actual error + stack on screen so you can debug what's failing.
 */
class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { hasError: boolean; error?: any; info?: any }> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: undefined, info: undefined };
  }
  static getDerivedStateFromError(error: any) {
    return { hasError: true, error };
  }
  componentDidCatch(error: any, info: any) {
    // also log to console
    console.error("ErrorBoundary caught:", error, info);
    this.setState({ error, info });
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 24, color: "crimson", fontFamily: "Inter, system-ui, sans-serif" }}>
          <h2>Something went wrong</h2>
          <pre style={{ whiteSpace: "pre-wrap", background: "#111", padding: 12, color: "#e6e6e6" }}>
            {String(this.state.error)}
            {"\n"}
            {this.state.info?.componentStack || ""}
          </pre>
        </div>
      );
    }
    return <>{this.props.children}</>;
  }
}

export default function CandidatesPage() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [jobFilter, setJobFilter] = useState<string>("");

  // defensive: ensure candidates state is always array
  useEffect(() => {
    fetchCandidates();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function fetchCandidates() {
    setLoading(true);
    setError(null);
    try {
      const url = new URL(`${API_BASE}/candidates/`);
      if (jobFilter) url.searchParams.set("job_id", jobFilter);
      const res = await fetch(url.toString());
      if (!res.ok) {
        // try to capture response text for debugging
        let body = "";
        try {
          body = await res.text();
        } catch (e) {
          /* ignore */
        }
        throw new Error(`Fetch failed: ${res.status} ${res.statusText} ${body ? "| body: " + body : ""}`);
      }
      const data = await res.json();
      // backend returns { total, limit, offset, candidates }
      if (!data || !Array.isArray(data.candidates)) {
        // defensive fallback
        console.warn("Unexpected /candidates response shape:", data);
        setCandidates([]);
      } else {
        setCandidates(data.candidates);
      }
    } catch (err: any) {
      console.error("fetchCandidates error:", err);
      setError(err?.message || String(err));
      setCandidates([]);
    } finally {
      setLoading(false);
    }
  }

  async function patchStatus(id?: number, status?: string) {
    if (!id) return;
    try {
      const res = await fetch(`${API_BASE}/candidates/${id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
      });
      if (!res.ok) {
        const txt = await res.text().catch(() => "");
        throw new Error(`Status update failed: ${res.status} ${txt}`);
      }
      // optimistic update locally
      setCandidates((prev) => prev.map((c) => (c._id === id ? { ...c, status } : c)));
    } catch (err: any) {
      console.error("patchStatus error:", err);
      alert("Failed to update status: " + (err.message || err));
    }
  }

  async function patchNotes(id?: number, notes?: string) {
    if (!id) return;
    try {
      const res = await fetch(`${API_BASE}/candidates/${id}/notes`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ notes }),
      });
      if (!res.ok) {
        const txt = await res.text().catch(() => "");
        throw new Error(`Notes update failed: ${res.status} ${txt}`);
      }
      setCandidates((prev) => prev.map((c) => (c._id === id ? { ...c, notes } : c)));
    } catch (err: any) {
      console.error("patchNotes error:", err);
      alert("Failed to update notes: " + (err.message || err));
    }
  }

  return (
    <ErrorBoundary>
      <main style={{ padding: 24, fontFamily: "Inter, system-ui, sans-serif" }}>
        <h1>Candidates</h1>

        <div style={{ marginBottom: 16, display: "flex", gap: 8, alignItems: "center" }}>
          <input
            placeholder="Filter by job id (e.g. JOB-001)"
            value={jobFilter}
            onChange={(e) => setJobFilter(e.target.value)}
          />
          <button onClick={() => fetchCandidates()}>Refresh</button>
          <button
            onClick={() => {
              setJobFilter("");
              fetchCandidates();
            }}
          >
            Clear filter
          </button>
        </div>

        {loading && <p>Loading candidates…</p>}
        {error && (
          <div style={{ color: "crimson", marginBottom: 12 }}>
            <strong>Error:</strong> {error}
          </div>
        )}

        <div style={{ overflowX: "auto" }}>
          <table style={{ borderCollapse: "collapse", width: "100%" }}>
            <thead>
              <tr>
                <th style={{ textAlign: "left", padding: 8, borderBottom: "1px solid #333" }}>#</th>
                <th style={{ textAlign: "left", padding: 8, borderBottom: "1px solid #333" }}>Name</th>
                <th style={{ textAlign: "left", padding: 8, borderBottom: "1px solid #333" }}>Email</th>
                <th style={{ textAlign: "left", padding: 8, borderBottom: "1px solid #333" }}>Score</th>
                <th style={{ textAlign: "left", padding: 8, borderBottom: "1px solid #333" }}>Missing skills</th>
                <th style={{ textAlign: "left", padding: 8, borderBottom: "1px solid #333" }}>Status</th>
                <th style={{ textAlign: "left", padding: 8, borderBottom: "1px solid #333" }}>Notes</th>
                <th style={{ textAlign: "left", padding: 8, borderBottom: "1px solid #333" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {candidates.length === 0 && !loading ? (
                <tr>
                  <td colSpan={8} style={{ padding: 12 }}>
                    No candidates found.
                  </td>
                </tr>
              ) : (
                candidates.map((c) => (
                  <tr key={c._id} style={{ borderBottom: "1px solid #222" }}>
                    <td style={{ padding: 8 }}>{c._id}</td>
                    <td style={{ padding: 8 }}>{c.name || "-"}</td>
                    <td style={{ padding: 8 }}>{c.email || "-"}</td>
                    <td style={{ padding: 8 }}>{c.total_score ?? "-"}</td>
                    <td style={{ padding: 8 }}>
                      {c.missing_skills ? (
                        <pre style={{ margin: 0 }}>{c.missing_skills}</pre>
                      ) : Array.isArray(c.questions) ? (
                        <pre style={{ margin: 0 }}>{c.questions.join("\n")}</pre>
                      ) : (
                        <pre style={{ margin: 0 }}>{String(c.questions || "-")}</pre>
                      )}
                    </td>
                    <td style={{ padding: 8 }}>
                      <select value={c.status || ""} onChange={(e) => patchStatus(c._id, e.target.value)}>
                        <option value="">unknown</option>
                        <option value="shortlisted">shortlisted</option>
                        <option value="review">review</option>
                        <option value="reject">reject</option>
                      </select>
                    </td>
                    <td style={{ padding: 8 }}>
                      <textarea
                        defaultValue={c.notes || ""}
                        rows={2}
                        style={{ width: 280 }}
                        onBlur={(e) => patchNotes(c._id, e.target.value)}
                      />
                    </td>
                    <td style={{ padding: 8 }}>
                      <button
                        onClick={() => {
                          // open candidate detail (backend has /candidates/{id})
                          window.open(`${API_BASE}/candidates/${c._id}`, "_blank");
                        }}
                      >
                        View JSON
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </main>
    </ErrorBoundary>
  );
}