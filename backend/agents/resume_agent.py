# backend/agents/resume_agent.py
from pathlib import Path
from typing import Dict, Any

from backend.utils import extract_contact_info

# External libs for .docx and .pdf parsing
try:
    from docx import Document  # python-docx
except Exception:
    Document = None

try:
    import pdfplumber  # pdfplumber
except Exception:
    pdfplumber = None


def _extract_text_from_docx(path: Path) -> str:
    if Document is None:
        return ""
    try:
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs if p.text])
    except Exception:
        return ""


def _extract_text_from_pdf(path: Path) -> str:
    if pdfplumber is None:
        return ""
    try:
        texts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    texts.append(page_text)
        return "\n".join(texts)
    except Exception:
        return ""


def _extract_text_from_txt(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def extract_resume_text_from_path(path: Path) -> str:
    """
    Safe extractor that supports .txt, .docx, .pdf.
    Returns the extracted text or empty string on failure.
    """
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".txt":
        return _extract_text_from_txt(p)
    if suffix == ".docx":
        return _extract_text_from_docx(p)
    if suffix == ".pdf":
        return _extract_text_from_pdf(p)

    # fallback: try reading as text
    return _extract_text_from_txt(p)


class ResumeAgent:
    """Loads resumes and extracts raw text + basic contact info."""

    def __init__(self, resume_path: Path) -> None:
        self.resume_path = Path(resume_path)

    def run(self) -> Dict[str, Any]:
        text = extract_resume_text_from_path(self.resume_path)
        contact = extract_contact_info(text)
        return {
            "path": str(self.resume_path),
            "text": text,
            "contact": contact,
        }