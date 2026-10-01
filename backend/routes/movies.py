from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.movie_service import (
    get_trending,
    search_movies,
    get_by_id,
    get_similar,
    get_recent_movies,
    get_sequels,
    get_marvel_movies,
    get_bollywood_tollywood,
)

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("/trending")
def trending(db: Session = Depends(get_db)):
    results = get_trending(db)
    return [
        {
            "movieId": m.movie_id,
            "title": m.title,
            "genres": m.genres,
            "poster_url": m.poster_url,
        }
        for m in results
    ]


@router.get("/search")
def search(q: str, db: Session = Depends(get_db)):
    results = search_movies(q, db)
    return [
        {
            "movieId": m.movie_id,
            "title": m.title,
            "genres": m.genres,
            "poster_url": m.poster_url,
        }
        for m in results
    ]


@router.get("/recent")
def recent(db: Session = Depends(get_db)):
    results = get_recent_movies(db)
    return [
        {
            "movieId": m.movie_id,
            "title": m.title,
            "genres": m.genres,
            "poster_url": m.poster_url,
        }
        for m in results
    ]


@router.get("/marvel")
def marvel(db: Session = Depends(get_db)):
    results = get_marvel_movies(db)
    return [
        {
            "movieId": m.movie_id,
            "title": m.title,
            "genres": m.genres,
            "poster_url": m.poster_url,
        }
        for m in results
    ]


@router.get("/indian-cinema")
def indian_cinema(db: Session = Depends(get_db)):
    results = get_bollywood_tollywood(db)
    return [
        {
            "movieId": m.movie_id,
            "title": m.title,
            "genres": m.genres,
            "poster_url": m.poster_url,
        }
        for m in results
    ]


@router.get("/{movie_id}")
def movie_details(movie_id: int, db: Session = Depends(get_db)):
    movie = get_by_id(movie_id, db)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {
        "movieId": movie.movie_id,
        "title": movie.title,
        "genres": movie.genres,
        "poster_url": movie.poster_url,
    }


@router.get("/{movie_id}/similar")
def similar(movie_id: int, db: Session = Depends(get_db)):
    results = get_similar(movie_id, db)
    return [
        {
            "movieId": m.movie_id,
            "title": m.title,
            "genres": m.genres,
            "poster_url": m.poster_url,
        }
        for m in results
    ]


@router.get("/{movie_id}/sequels")
def sequels(movie_id: int, db: Session = Depends(get_db)):
    results = get_sequels(movie_id, db)
    return [
        {
            "movieId": m.movie_id,
            "title": m.title,
            "genres": m.genres,
            "poster_url": m.poster_url,
        }
        for m in results
    ]
