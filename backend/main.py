from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging
import os

from backend.database import Base, engine
from backend.routes import users, movies, ratings, watchlist, recommendations, ai

# Ensure schema exists safely
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MovieMatch API", description="Next-Gen AI Recommendation Engine")

# Exception handler for zero-fault tolerance
logger = logging.getLogger("uvicorn.error")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500, content={"detail": "Internal server error gracefully handled."}
    )


# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for local poster caching
os.makedirs("static/posters", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include modular routes
app.include_router(users.router)
app.include_router(movies.router)
app.include_router(ratings.router)
app.include_router(watchlist.router)
app.include_router(recommendations.router)
app.include_router(ai.router)


@app.get("/")
def health_check():
    return {"status": "MovieMatch API is running"}
