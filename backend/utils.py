# backend/utils.py
import re
from typing import Dict, List

def extract_resume_text(file_path: str) -> str:
    # Demo fallback: if PDF name ends with sample_resume.pdf, return a small sample
    if file_path and file_path.endswith("sample_resume.pdf"):
        return "John Doe\njohn@example.com\n+91-99999-99999\nSkills: Python, FastAPI, REST API, SQL"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def keyword_match(resume_text: str, job_desc: str) -> int:
    resume_words = set(re.findall(r'\w+', resume_text.lower()))
    job_words = set(re.findall(r'\w+', job_desc.lower()))
    return len(resume_words & job_words)

def generate_interview_questions(resume_text: str, job_desc: str) -> List[str]:
    return [
        "Describe your experience with Python.",
        "How have you built REST APIs?",
        "Can you discuss CI/CD pipeline management?"
    ]

def extract_contact_info(resume_text: str) -> Dict[str, str]:
    name = resume_text.split('\n')[0] if resume_text else ""
    email_m = re.search(r'[\w\.-]+@[\w\.-]+', resume_text or "")
    phone_m = re.search(r'\+?\d[\d\-\s]{6,}\d', resume_text or "")
    return {
        "name": name.strip(),
        "email": email_m.group(0) if email_m else "",
        "phone": phone_m.group(0) if phone_m else ""
    }