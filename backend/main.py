# backend/main.py
from fastapi import FastAPI, UploadFile, File, Query, HTTPException, Path as FastAPIPath
from fastapi.responses import FileResponse, JSONResponse
from backend.recruitgenie_app import process_candidate, load_job_description
from backend.agents.data_agent import DataAgent
from pathlib import Path
import shutil
import csv
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from collections import Counter

app = FastAPI(title="RecruitGenie API")

# Where uploaded resumes are stored (same as used elsewhere)
UPLOAD_DIR = Path("backend/assets/resumes")
OUTPUT_PATH = Path("backend/assets/candidate_data.csv")

# Columns expected in CSV (DataAgent writes these). Keep consistent with DataAgent.
CSV_HEADER = [
    "job_id",
    "name",
    "email",
    "phone",
    "total_score",
    "base_score",
    "skill_score",
    "penalty",
    "questions",
    "status",
    "notes",
]

# -------------------------
# Utility CSV helpers
# -------------------------
def _read_csv(path: Path) -> List[Dict[str, str]]:
    """Read CSV into list of dicts. Always returns rows in file order."""
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            # ensure all expected keys exist
            row = {k: (v if v is not None else "") for k, v in r.items()}
            for h in CSV_HEADER:
                if h not in row:
                    row[h] = ""
            rows.append(row)
    return rows


def _write_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    """Write rows to CSV (overwrites). Ensure header order."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        writer.writeheader()
        for r in rows:
            # ensure keys
            out = {k: (str(r.get(k, "")) if r.get(k, "") is not None else "") for k in CSV_HEADER}
            writer.writerow(out)


def _safe_int(val: str, default: int = 0) -> int:
    try:
        return int(val)
    except Exception:
        try:
            return int(float(val))
        except Exception:
            return default


# -------------------------
# Health / Root
# -------------------------
@app.get("/")
def root() -> Dict[str, Any]:
    """Simple health / root endpoint: shows available endpoints."""
    return {"status": "ok", "service": "RecruitGenie API", "endpoints": ["/docs", "/upload_resume/", "/candidates/"]}


# -------------------------
# Upload & process resume
# -------------------------
@app.post("/upload_resume/")
async def upload_resume(job_id: str = Query(..., description="Job ID"), file: UploadFile = File(...)):
    """
    Upload a resume file (multipart/form-data) and process it for the given job_id.
    Returns the processing result (score, generated questions, status, etc.)
    The response also returns the stored filename so the frontend can call the resume download endpoint.
    """
    # Save the uploaded file
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    resume_path = UPLOAD_DIR / file.filename

    # Write the incoming file to disk (overwrites if same name)
    with open(resume_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Load job description (may raise FileNotFoundError handled by caller)
    job_desc = load_job_description()

    # Use DataAgent to append CSV row (DataAgent handles header creation)
    data_agent = DataAgent(OUTPUT_PATH)
    result = process_candidate(job_id, job_desc, resume_path, data_agent)

    # Attach the saved filename so frontend can call download endpoint
    result_with_file = dict(result)
    result_with_file["saved_filename"] = resume_path.name

    return {
        "message": "Resume processed successfully!",
        "file": resume_path.name,
        "result": result_with_file,
    }


# -------------------------
# Serve saved resume file
# -------------------------
@app.get("/resumes/file/{filename}")
def download_resume_file(filename: str):
    """
    Serve a saved resume file from backend/assets/resumes/.
    Use the stored filename returned by upload_resume (result.saved_filename).
    This endpoint performs a simple safety check to avoid path-traversal.
    """
    # sanitize: use only the final name part (no directories allowed)
    safe_name = Path(filename).name
    file_path = UPLOAD_DIR / safe_name

    if not file_path.exists() or not file_path.is_file():
        return JSONResponse(status_code=404, content={"detail": "file not found"})

    # let the client download; set generic binary media type so browsers prompt to download
    return FileResponse(file_path, filename=safe_name, media_type="application/octet-stream")


# -------------------------
# Candidate listing (CSV)
# -------------------------
@app.get("/candidates/")
def list_candidates(
    job_id: Optional[str] = Query(None, description="Filter by job_id"),
    status: Optional[str] = Query(None, description="Filter by status (shortlisted/review/reject)"),
    limit: int = Query(50, ge=1, le=500, description="Max rows to return"),
    offset: int = Query(0, ge=0, description="Rows to skip"),
) -> Dict[str, Any]:
    """
    Return candidate rows from the CSV as JSON with optional filters and pagination.
    If CSV doesn't exist yet, returns empty list.
    Each candidate will get a stable `id` equal to its 1-based row index in the CSV.
    """
    rows = _read_csv(OUTPUT_PATH)

    filtered = []
    for idx, r in enumerate(rows, start=1):
        # apply filters
        if job_id and (r.get("job_id", "") != job_id):
            continue
        if status and (r.get("status", "").lower() != status.lower()):
            continue
        # annotate with id
        rr = dict(r)
        rr["_id"] = idx
        filtered.append(rr)

    total = len(filtered)
    sliced = filtered[offset: offset + limit]
    return {"total": total, "limit": limit, "offset": offset, "candidates": sliced}


# -------------------------
# Candidate detail & updates
# -------------------------
@app.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: int = FastAPIPath(..., ge=1)):
    """Return a single candidate by its CSV row index (1-based)."""
    rows = _read_csv(OUTPUT_PATH)
    if candidate_id < 1 or candidate_id > len(rows):
        raise HTTPException(status_code=404, detail="Candidate not found")
    row = dict(rows[candidate_id - 1])
    # parse some numeric fields into ints for convenience
    row["total_score"] = _safe_int(row.get("total_score", "0"))
    row["base_score"] = _safe_int(row.get("base_score", "0"))
    row["skill_score"] = _safe_int(row.get("skill_score", "0"))
    row["penalty"] = _safe_int(row.get("penalty", "0"))
    row["_id"] = candidate_id
    # Questions stored as joined string -> split
    questions_raw = row.get("questions", "")
    row["questions"] = [q.strip() for q in questions_raw.split(" | ") if q.strip()]
    return row


class StatusPayload(BaseModel):
    status: str


class NotesPayload(BaseModel):
    notes: str


@app.patch("/candidates/{candidate_id}/status")
def update_status(candidate_id: int, payload: StatusPayload):
    """Update the 'status' field (shortlisted/reject/review)."""
    rows = _read_csv(OUTPUT_PATH)
    if candidate_id < 1 or candidate_id > len(rows):
        raise HTTPException(status_code=404, detail="Candidate not found")
    rows[candidate_id - 1]["status"] = payload.status
    _write_csv(OUTPUT_PATH, rows)
    return {"ok": True, "id": candidate_id, "status": payload.status}


@app.patch("/candidates/{candidate_id}/notes")
def update_notes(candidate_id: int, payload: NotesPayload):
    """Update free-form notes for a candidate."""
    rows = _read_csv(OUTPUT_PATH)
    if candidate_id < 1 or candidate_id > len(rows):
        raise HTTPException(status_code=404, detail="Candidate not found")
    rows[candidate_id - 1]["notes"] = payload.notes
    _write_csv(OUTPUT_PATH, rows)
    return {"ok": True, "id": candidate_id}


# -------------------------
# Analytics endpoints
# -------------------------
@app.get("/analytics/summary")
def analytics_summary(job_id: Optional[str] = Query(None, description="Optional job filter")) -> Dict[str, Any]:
    """
    Return quick analytics summary:
     - total candidates
     - average score
     - counts by status
     - top missing skills (aggregated)
    """
    rows = _read_csv(OUTPUT_PATH)
    if job_id:
        rows = [r for r in rows if r.get("job_id", "") == job_id]

    total = len(rows)
    if total == 0:
        return {"total": 0, "avg_score": 0.0, "status_counts": {}, "top_missing_skills": []}

    scores = [_safe_int(r.get("total_score", "0")) for r in rows]
    avg_score = sum(scores) / total if total else 0.0
    status_counts = Counter(r.get("status", "").lower() or "unknown" for r in rows)

    missing = Counter()
    for r in rows:
        ms_raw = r.get("missing_skills", "")
        # DataAgent used " | " join; accept comma/pipe/semicolon splits
        parts = [p.strip() for delim in ["|", ";", ","] for p in ms_raw.split(delim)]
        for p in parts:
            if not p:
                continue
            missing[p.lower()] += 1

    top_missing = missing.most_common(20)

    # return convenient JSON
    return {
        "total": total,
        "avg_score": round(avg_score, 2),
        "status_counts": dict(status_counts),
        "top_missing_skills": [{"skill": k, "count": v} for k, v in top_missing],
    }


# Allow frontend dev server to call API
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)