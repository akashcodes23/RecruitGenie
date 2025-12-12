# backend/api/endpoints.py
from fastapi import APIRouter, UploadFile, File
from typing import List, Dict
from pathlib import Path

from backend.recruitgenie_app import orchestrate, RESUMES_DIR

router = APIRouter(prefix="/api", tags=["RecruitGenie"])


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)) -> Dict[str, str]:
    RESUMES_DIR.mkdir(parents=True, exist_ok=True)
    dest = RESUMES_DIR / file.filename
    content = await file.read()
    dest.write_bytes(content)
    return {"message": "Resume uploaded successfully", "filename": file.filename}


@router.post("/run-screening")
async def run_screening(job_id: str = "JOB-001") -> Dict[str, List[Dict]]:
    results = orchestrate(job_id=job_id)
    return {"job_id": job_id, "results": results}