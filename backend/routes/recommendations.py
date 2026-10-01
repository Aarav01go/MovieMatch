from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.recommendation_service import recommendation_service

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/{user_id}")
def get_recs(user_id: int, algo: str = "svd", db: Session = Depends(get_db)):
    try:
        return recommendation_service.get_recommendations(user_id, algo, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/match/{user1_id}/{user2_id}")
def matchmaker(
    user1_id: int, user2_id: int, algo: str = "svd", db: Session = Depends(get_db)
):
    try:
        results = recommendation_service.get_mutual_recommendations(
            user1_id, user2_id, db, algo
        )
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
