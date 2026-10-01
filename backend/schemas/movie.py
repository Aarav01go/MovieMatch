from pydantic import BaseModel, Field
from typing import Optional


class MovieResponse(BaseModel):
    movieId: int
    title: str
    genres: str
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    rating: Optional[float] = None


class RatingSchema(BaseModel):
    user_id: int
    movie_id: int
    rating: float = Field(..., ge=1.0, le=5.0)


class WatchlistSchema(BaseModel):
    user_id: int
    movie_id: int
