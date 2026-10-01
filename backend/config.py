import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")
    OMDB_API_KEY = os.environ.get("OMDB_API_KEY", "thewdb")
    DATABASE_URL = os.environ.get(
        "DATABASE_URL", "sqlite:///backend/data/moviematch.db"
    )
    APP_ENV = os.environ.get("APP_ENV", "development")


settings = Settings()
