from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.watchlist import Watchlist
from backend.models.movie import Movie
from backend.schemas.movie import WatchlistSchema

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


@router.post("")
def add_to_watchlist(item: WatchlistSchema, db: Session = Depends(get_db)):
    existing = (
        db.query(Watchlist)
        .filter(Watchlist.user_id == item.user_id, Watchlist.movie_id == item.movie_id)
        .first()
    )
    if not existing:
        new_item = Watchlist(user_id=item.user_id, movie_id=item.movie_id)
        db.add(new_item)
        db.commit()
    return {"status": "success"}


@router.get("/{user_id}")
def get_watchlist(user_id: int, db: Session = Depends(get_db)):
    items = (
        db.query(Watchlist, Movie)
        .join(Movie, Watchlist.movie_id == Movie.movie_id)
        .filter(Watchlist.user_id == user_id)
        .all()
    )
    return [
        {
            "movieId": m.movie_id,
            "title": m.title,
            "genres": m.genres,
            "poster_url": m.poster_url,
        }
        for w, m in items
    ]
