# backend/recruitgenie_app.py

from backend.agents.resume_agent import ResumeAgent
from backend.agents.scoring_agent import ScoringAgent
from backend.agents.interview_agent import InterviewAgent
from backend.agents.data_agent import DataAgent
from pathlib import Path
from typing import List, Dict, Any
import traceback

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
RESUMES_DIR = ASSETS_DIR / "resumes"
JOB_DESC_PATH = ASSETS_DIR / "job_description.txt"
OUTPUT_PATH = ASSETS_DIR / "candidate_data.csv"


def load_job_description() -> str:
    """Read and return the job description text. Raises FileNotFoundError if missing."""
    if not JOB_DESC_PATH.exists():
        raise FileNotFoundError(f"Job description not found at {JOB_DESC_PATH}")
    return JOB_DESC_PATH.read_text(encoding="utf-8")


def find_resume_files() -> List[Path]:
    """Return list of resume files (pdf, docx and text) in the resumes directory."""
    RESUMES_DIR.mkdir(parents=True, exist_ok=True)
    files = list(RESUMES_DIR.glob("*.pdf")) + list(RESUMES_DIR.glob("*.txt")) + list(RESUMES_DIR.glob("*.docx"))
    return files


def process_candidate(
    job_id: str, job_desc: str, resume_path: Path, data_agent: DataAgent
) -> Dict[str, Any]:
    """Process a single resume using the agents and return a result dict.

    This function is defensive: it validates agent outputs and builds fallbacks
    so a single bad resume or bug does not crash the whole batch run.
    """
    try:
        # Extract resume text and contact info
        resume_agent = ResumeAgent(resume_path)
        resume_data = resume_agent.run()

        if not isinstance(resume_data, dict) or "text" not in resume_data:
            raise ValueError(f"resume_agent.run() returned unexpected value: {resume_data!r}")

        # Score the resume
        scoring_agent = ScoringAgent(job_desc)
        score = scoring_agent.run(resume_data.get("text", ""))

        # Normalize score to expected keys
        if not isinstance(score, dict):
            raise ValueError(f"ScoringAgent.run() should return dict, got: {type(score)}")

        expected_keys = {"base_score", "skill_score", "penalty", "total_score", "missing_skills", "found_skills"}
        missing = expected_keys - set(score.keys())
        if missing:
            print(f"[WARN] ScoringAgent result missing keys: {missing}. Full score: {score}")
            base_score = score.get("base_score") or score.get("total_score") or 0
            score = {
                "base_score": base_score,
                "skill_score": score.get("skill_score", 0),
                "penalty": score.get("penalty", 0),
                "total_score": score.get("total_score", base_score),
                "missing_skills": score.get("missing_skills", []),
                "found_skills": score.get("found_skills", []),
            }

        # Generate interview questions
        interview_agent = InterviewAgent(job_title="Backend Engineer")
        questions = interview_agent.run(
            missing_skills=score.get("missing_skills", []), found_skills=score.get("found_skills", [])
        )

        # Persist results and capture derived status (shortlisted/review/reject)
        saved_filename = resume_path.name
        status = data_agent.append_result(job_id, resume_data.get("contact", {}), score, questions, saved_filename)

        return {
            "job_id": job_id,
            "file": str(resume_path.name),
            "contact": resume_data.get("contact", {}),
            "score": score,
            "questions": questions,
            "status": status,
            "saved_filename": saved_filename,
        }

    except Exception as e:
        print(f"[ERROR] processing {resume_path}: {e}")
        traceback.print_exc()
        return {
            "job_id": job_id,
            "file": str(resume_path.name),
            "contact": {},
            "score": {"total_score": 0},
            "questions": [],
            "status": "error",
            "error": str(e),
            "saved_filename": str(resume_path.name),
        }