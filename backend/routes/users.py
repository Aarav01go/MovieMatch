from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.models.rating import Rating
from backend.schemas.user import UserSchema

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("")
def get_or_create_user(user: UserSchema, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        db_user = User(username=user.username)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    return {"user_id": db_user.user_id, "username": db_user.username}


@router.get("/{user_id}/stats")
def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    ratings_count = db.query(Rating).filter(Rating.user_id == user_id).count()
    return {"username": db_user.username, "ratings_count": ratings_count}
