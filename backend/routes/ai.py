from fastapi import APIRouter, HTTPException
from schemas.recommendation import MoodRequest
from schemas.ai import AIAssistantRequest
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from services.ai_service import get_ai_recommendation
from services.ai_service import generate_synopsis, rerank_movies_by_mood

router = APIRouter(prefix="/ai", tags=["AI Features"])


@router.get("/synopsis")
def get_synopsis(title: str):
    return {"synopsis": generate_synopsis(title)}


@router.post("/rerank")
def rerank(req: MoodRequest):
    try:
        return {"result": rerank_movies_by_mood(req.movies, req.mood)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assistant")
def chat_assistant(req: AIAssistantRequest, db: Session = Depends(get_db)):
    return get_ai_recommendation(req.query, db)
