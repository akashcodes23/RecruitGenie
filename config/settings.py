import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    POSTGRES_URL = os.getenv("POSTGRES_URL")
    MONGODB_URL = os.getenv("MONGODB_URL")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

settings = Settings()

