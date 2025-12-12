// recruitgenie-frontend/app/upload/page.tsx
"use client";

import React, { useState } from "react";

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE as string) || "http://127.0.0.1:8001";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string>("JOB-001");
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setResult(null);
    setError(null);

    if (!file) {
      setError("Please choose a file.");
      return;
    }

    setLoading(true);

    const fd = new FormData();
    fd.append("file", file);

    // job_id is a query param on backend endpoint
    const url = `${API_BASE}/upload_resume/?job_id=${encodeURIComponent(jobId)}`;

    try {
      const res = await fetch(url, {
        method: "POST",
        body: fd,
      });

      // attempt to parse JSON body safely
      let data: any = null;
      try {
        data = await res.json();
      } catch (err) {
        const text = await res.text().catch(() => "");
        throw new Error(`Non-JSON response: ${res.status} ${res.statusText} ${text}`);
      }

      if (!res.ok) {
        // backend returned error payload
        throw new Error(
          typeof data === "string" ? data : JSON.stringify(data, null, 2) || `${res.status} ${res.statusText}`
        );
      }

      setResult(data);
    } catch (err: any) {
      setError(err?.message ?? String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ padding: 24, maxWidth: 820, fontFamily: "Inter, system-ui, sans-serif" }}>
      <h1>Upload Resume</h1>

      <form onSubmit={handleSubmit}>
        <label style={{ display: "block", marginBottom: 8 }}>
          <strong>Job ID:</strong>
          <input
            value={jobId}
            onChange={(e) => setJobId(e.target.value)}
            style={{ marginLeft: 8, padding: 6 }}
            aria-label="job-id"
          />
        </label>

        <label style={{ display: "block", marginTop: 12 }}>
          <strong>Choose file:</strong>
          <input
            type="file"
            onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
            accept=".pdf,.txt,.docx"
            style={{ display: "block", marginTop: 8 }}
          />
        </label>

        <div style={{ marginTop: 12 }}>
          <button type="submit" disabled={loading} style={{ padding: "8px 12px" }}>
            {loading ? "Uploading..." : "Upload & Process"}
          </button>
        </div>
      </form>

      {error && (
        <pre style={{ color: "crimson", marginTop: 12, whiteSpace: "pre-wrap", background: "#111", padding: 12 }}>
          {error}
        </pre>
      )}

      {result && (
        <div style={{ marginTop: 12 }}>
          <h3>Result</h3>
          <pre
            style={{
              maxHeight: 360,
              overflow: "auto",
              background: "#111",
              color: "#e6e6e6",
              padding: 12,
              whiteSpace: "pre-wrap",
            }}
          >
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </