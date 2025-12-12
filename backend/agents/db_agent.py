# backend/agents/db_agent.py
from typing import Dict, Any, List
from backend.db import get_engine, candidates
from sqlalchemy import insert, select, update

class DBAgent:
    def __init__(self):
        self.engine = get_engine()

    def add_candidate(self, job_id: str, file: str, contact: Dict[str,str], score: Dict[str,Any], questions: List[str]) -> int:
        stmt = insert(candidates).values(
            job_id=job_id,
            file=file,
            name=contact.get("name",""),
            email=contact.get("email",""),
            phone=contact.get("phone",""),
            score=score,
            questions=questions,
            status="applied",
            notes=""
        )
        with self.engine.connect() as conn:
            res = conn.execute(stmt)
            conn.commit()
            return res.inserted_primary_key[0]

    def update_status(self, candidate_id: int, status: str):
        stmt = update(candidates).where(candidates.c.id==candidate_id).values(status=status)
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def update_notes(self, candidate_id: int, notes: str):
        stmt = update(candidates).where(candidates.c.id==candidate_id).values(notes=notes)
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def list_candidates(self, job_id=None, status=None, limit=50, offset=0):
        stmt = select(candidates)
        if job_id:
            stmt = stmt.where(candidates.c.job_id==job_id)
        if status:
            stmt = stmt.where(candidates.c.status==status)
        stmt = stmt.limit(limit).offset(offset)
        with self.engine.connect() as conn:
            rows = conn.execute(stmt).mappings().all()
            return [dict(r) for r in rows]

    def get_candidate(self, candidate_id: int):
        stmt = select(candidates).where(candidates.c.id==candidate_id)
        with self.engine.connect() as conn:
            row = conn.execute(stmt).mappings().first()
            return dict(row) if row else None