import sys
import os

# Add backend/ to Python path so all bare imports (database, models, etc.) resolve correctly
# This is needed when uvicorn is invoked from the repo root as: uvicorn backend.main:app
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging
import os

from database import Base, engine
from routes import users, movies, ratings, watchlist, recommendations, ai

# Ensure DB schema exists
Base.metadata.create_all(bind=engine)

# Ensure static poster directory exists (needed on Render's ephemeral disk)
os.makedirs("static/posters", exist_ok=True)

app = FastAPI(title="MovieMatch API", description="Next-Gen AI Recommendation Engine")

logger = logging.getLogger("uvicorn.error")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500, content={"detail": "Internal server error gracefully handled."}
    )


# CORS — allow localhost dev + any Vercel deployment URL
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]

# Allow all Vercel preview + production URLs for this project
ALLOWED_ORIGIN_REGEX = r"https://.*\.vercel\.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=ALLOWED_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve locally cached posters
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(users.router)
app.include_router(movies.router)
app.include_router(ratings.router)
app.include_router(watchlist.router)
app.include_router(recommendations.router)
app.include_router(ai.router)


@app.get("/")
def health_check():
    return {"status": "MovieMatch API is running", "version": "1.0.0"}
