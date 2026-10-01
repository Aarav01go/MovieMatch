from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.rating import Rating
from backend.models.movie import Movie
from backend.schemas.movie import RatingSchema

router = APIRouter(prefix="/ratings", tags=["Ratings"])


@router.post("")
def add_rating(rating: RatingSchema, db: Session = Depends(get_db)):
    new_rating = Rating(
        user_id=rating.user_id, movie_id=rating.movie_id, rating=rating.rating
    )
    db.add(new_rating)
    db.commit()
    return {"status": "success"}


@router.get("/{user_id}")
def get_ratings(user_id: int, db: Session = Depends(get_db)):
    ratings = (
        db.query(Rating, Movie)
        .join(Movie, Rating.movie_id == Movie.movie_id)
        .filter(Rating.user_id == user_id)
        .all()
    )
    return [
        {
            "movieId": m.movie_id,
            "title": m.title,
            "genres": m.genres,
            "rating": r.rating,
            "poster_url": m.poster_url,
        }
        for r, m in ratings
    ]
