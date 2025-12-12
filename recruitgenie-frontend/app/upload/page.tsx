"use client";
import { useState } from "react";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState("JOB-001");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const API_ORIGIN = "http://127.0.0.1:8001"; // update if needed

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return alert("Choose a file first");
    setLoading(true);
    const fd = new FormData();
    fd.append("file", file);
    const url = `${API_ORIGIN}/upload_resume/?job_id=${encodeURIComponent(jobId)}`;
    try {
      const res = await fetch(url, { method: "POST", body: fd });
      const json = await res.json();
      setResult(json);
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ padding: 20 }}>
      <h2>Upload resume</h2>
      <form onSubmit={handleUpload}>
        <div>
          <label>Job ID: <input value={jobId} onChange={e => setJobId(e.target.value)} /></label>
        </div>
        <div>
          <input type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        </div>
        <button type="submit" disabled={loading}>{loading ? "Uploading..." : "Upload"}</button>
      </form>

      {result && (
        <div style={{ marginTop: 20 }}>
          <h3>Result</h3>
          <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </main>
  );
}