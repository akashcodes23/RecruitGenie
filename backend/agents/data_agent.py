# backend/agents/data_agent.py
from pathlib import Path
from typing import Dict, List
import csv

class DataAgent:
    """Stores candidate results (e.g., CSV)."""

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def append_result(
        self,
        job_id: str,
        contact: Dict[str, str],
        score: Dict[str, int],
        questions: List[str],
        saved_filename: str = "",
    ) -> None:
        header = [
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
            "saved_filename",
        ]

        file_exists = self.output_path.exists()

        with self.output_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(header)
            writer.writerow(
                [
                    job_id,
                    contact.get("name", ""),
                    contact.get("email", ""),
                    contact.get("phone", ""),
                    score.get("total_score", 0),
                    score.get("base_score", 0),
                    score.get("skill_score", 0),
                    score.get("penalty", 0),
                    " | ".join(questions),
                    "",  # status
                    "",  # notes
                    saved_filename,
                ]
            )