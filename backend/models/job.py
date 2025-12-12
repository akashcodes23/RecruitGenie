from pydantic import BaseModel

class Job(BaseModel):
    title: str
    description: str
    requirements: str
    location: str
    salary_min: int = 0
    salary_max: int = 0

