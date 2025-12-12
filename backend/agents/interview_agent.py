# backend/agents/interview_agent.py
from typing import List


class InterviewAgent:
    """Generates personalized interview questions based on skill gaps."""

    def __init__(self, job_title: str = "Engineer") -> None:
        self.job_title = job_title

    def run(self, missing_skills: List[str], found_skills: List[str]) -> List[str]:
        questions: List[str] = []

        # Gap-based questions
        for skill in missing_skills[:5]:
            questions.append(
                f"Can you walk me through any experience you have with {skill}, "
                "or how you would learn it quickly?"
            )

        # Deep-dive questions on strong skills
        for skill in found_skills[:3]:
            questions.append(
                f"Can you describe a project where you used {skill} end-to-end?"
            )

        # Generic behavioral / system questions
        questions.extend(
            [
                f"What do you consider your strongest contribution as a {self.job_title} so far?",
                "Tell me about a time you dealt with a production issue or critical bug."
            ]
        )

        return questions