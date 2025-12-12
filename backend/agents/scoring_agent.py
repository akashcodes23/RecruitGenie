# backend/agents/scoring_agent.py
import os
from typing import Dict, Any, List
import re
from pathlib import Path

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_AI = bool(OPENAI_API_KEY)

if USE_AI:
    import openai
    openai.api_key = OPENAI_API_KEY

class ScoringAgent:
    def __init__(self, job_desc: str):
        self.job_desc = job_desc.lower()

        # baseline skill list - you can load from JSON config
        self.skill_list = ["python","sql","rest api","api","docker","aws","kubernetes","django","flask","graphql"]

    def _rule_score(self, text: str) -> Dict[str,Any]:
        text_l = text.lower()
        found = [s for s in self.skill_list if s in text_l]
        missing = [s for s in self.skill_list if s not in text_l]
        base = 5
        skill_score = len(found) * 2
        penalty = 0
        total = base + skill_score - penalty
        return {"base_score": base, "skill_score": skill_score, "penalty": penalty, "total_score": total, "missing_skills": missing, "found_skills": found}

    async def _ai_score(self, text: str) -> Dict[str,Any]:
        # Simple prompt (tailor to your provider)
        prompt = f"""
You are an assistant that reads a resume text and a job description and returns a JSON object:
{{"base_score":int,"skill_score":int,"penalty":int,"total_score":int,"missing_skills":[...],"found_skills":[...]}}

Job description:
{self.job_desc}

Resume text:
{text}
"""
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":"You are an expert recruiter scorer."},{"role":"user","content":prompt}],
            max_tokens=300
        )
        content = resp["choices"][0]["message"]["content"]
        # parse JSON from content (be defensive) - use regex or json.loads if well-formed
        import json, re
        try:
            j = json.loads(re.search(r"\{.*\}", content, re.S).group(0))
            return j
        except Exception:
            # fallback to rule scoring
            return self._rule_score(text)

    def run(self, resume_text: str) -> Dict[str,Any]:
        if USE_AI:
            import asyncio
            return asyncio.get_event_loop().run_until_complete(self._ai_score(resume_text))
        else:
            return self._rule_score(resume_text)