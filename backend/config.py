import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENROUTER_KEY: str = os.environ.get("OPENROUTER_KEY", "")
    OMDB_API_KEY: str = os.environ.get("OMDB_API_KEY", "thewdb")
    # On Render the working directory IS the repo root, so this path works
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL", "sqlite:///backend/data/moviematch.db"
    )
    APP_ENV: str = os.environ.get("APP_ENV", "development")


settings = Settings()
