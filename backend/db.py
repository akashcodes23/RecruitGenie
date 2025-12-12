# backend/db.py
from pathlib import Path
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, JSON, Text
from sqlalchemy.sql import select
from sqlalchemy.engine import Engine

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "recruitgenie.sqlite"
ENGINE = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
metadata = MetaData()

candidates = Table(
    "candidates",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("job_id", String, index=True),
    Column("file", String),
    Column("name", String),
    Column("email", String),
    Column("phone", String),
    Column("score", JSON),     # stores dict with base_score, skill_score, penalty, total_score, missing_skills, found_skills
    Column("questions", JSON),
    Column("status", String, default="applied"),  # applied/review/shortlisted/rejected
    Column("notes", Text, default=""),
)

def init_db():
    metadata.create_all(ENGINE)

def get_engine() -> Engine:
    return ENGINE