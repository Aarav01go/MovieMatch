from fastapi import FastAPI, HTTPException, Depends
import pickle
from typing import List
from sqlalchemy.orm import Session
from backend.database import get_db, User, Movie, Rating


import requests

import os
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")

def call_openrouter(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "google/gemini-2.5-flash",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

app = FastAPI(title="MovieMatch API")

# Load Models
models = {}
for algo in ['svd', 'knn', 'baseline']:
    try:
        with open(f"backend/models/{algo}_model.pkl", "rb") as f:
            models[algo] = pickle.load(f)
    except:
        models[algo] = None

from pydantic import BaseModel, Field

class UserSchema(BaseModel):
    username: str

class RatingSchema(BaseModel):
    user_id: int
    movie_id: int
    rating: float = Field(..., ge=1.0, le=5.0)

class MoodRequest(BaseModel):
    movies: List[str]
    mood: str

@app.post("/users")
def get_or_create_user(user: UserSchema, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        db_user = User(username=user.username)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    return {"user_id": db_user.user_id, "username": db_user.username}

@app.get("/movies/search")
def search_movies(q: str, db: Session = Depends(get_db)):
    # Search database
    results = db.query(Movie).filter(Movie.title.ilike(f"%{q}%")).limit(12).all()
    if not results:
        try:
            prompt = f"Provide details for a real movie matching '{q}'. Format exactly as: Title|Genre1,Genre2. If it is not a real movie, return exactly 'NOT_FOUND'."

            response_text = call_openrouter(prompt).strip()
            if "NOT_FOUND" not in response_text and "|" in response_text:
                title, genres = response_text.split("|", 1)

                title, genres = title.strip(), genres.strip()
                
                # Check exact match
                exact = db.query(Movie).filter(Movie.title.ilike(title)).first()
                if exact:
                    return [{"movieId": exact.movie_id, "title": exact.title, "genres": exact.genres}]
                    
                # Get max movie ID (or fake high one) and insert
                max_id = db.query(Movie).order_by(Movie.movie_id.desc()).first()
                new_id = (max_id.movie_id + 1) if max_id else 1
                
                new_movie = Movie(movie_id=new_id, title=title, genres=genres)
                db.add(new_movie)
                db.commit()
                db.refresh(new_movie)
                
                return [{"movieId": new_movie.movie_id, "title": new_movie.title, "genres": new_movie.genres}]
        except Exception:
            pass
            
    return [{"movieId": m.movie_id, "title": m.title, "genres": m.genres} for m in results]

@app.get("/movies/trending")
def trending_movies(db: Session = Depends(get_db)):
    # Quick pseudo-random sample in SQL
    from sqlalchemy.sql.expression import func
    results = db.query(Movie).order_by(func.random()).limit(6).all()
    return [{"movieId": m.movie_id, "title": m.title, "genres": m.genres} for m in results]

@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: int, algo: str = "svd", db: Session = Depends(get_db)):
    if algo not in models or models[algo] is None:
        raise HTTPException(status_code=400, detail="Model not found or not trained")
    
    model = models[algo]
    from sqlalchemy.sql.expression import func
    sample_movies = db.query(Movie).order_by(func.random()).limit(200).all()
    
    predictions = []
    for m in sample_movies:
        pred = model.predict(uid=user_id, iid=m.movie_id)
        predictions.append({
            "movieId": m.movie_id,
            "title": m.title,
            "genres": m.genres,
            "rating": pred.est
        })
    
    predictions.sort(key=lambda x: x['rating'], reverse=True)
    return predictions[:12]

@app.post("/ratings")
def add_rating(rating: RatingSchema, db: Session = Depends(get_db)):
    new_rating = Rating(user_id=rating.user_id, movie_id=rating.movie_id, rating=rating.rating)
    db.add(new_rating)
    db.commit()
    return {"status": "success"}

@app.get("/ratings/{user_id}")
def get_ratings(user_id: int, db: Session = Depends(get_db)):
    ratings = db.query(Rating, Movie).join(Movie, Rating.movie_id == Movie.movie_id).filter(Rating.user_id == user_id).all()
    return [{"movieId": m.movie_id, "title": m.title, "genres": m.genres, "rating": r.rating, "timestamp": r.timestamp} for r, m in ratings]

@app.get("/ai/synopsis")
def get_synopsis(title: str):
    try:
        response_text = call_openrouter(f"Write a 2-sentence captivating synopsis for '{title}'.")
        return {"synopsis": response_text}
    except Exception as e:
        return {"synopsis": "Synopsis unavailable."}

@app.post("/ai/rerank")
def rerank_by_mood(req: MoodRequest):
    try:
        titles = ", ".join(req.movies)
        prompt = f"Movies: {titles}. User's mood: '{req.mood}'. Re-order to best match. Return a numbered list."
        response_text = call_openrouter(prompt)
        return {"result": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/movies/similar/{movie_id}")
def similar_movies(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    genres = movie.genres.split('|') if movie.genres else []
    similar = []
    from sqlalchemy.sql.expression import func
    if genres:
        from sqlalchemy import or_
        genre_filter = or_(*[Movie.genres.ilike(f"%{g.strip()}%") for g in genres])
        similar = db.query(Movie).filter(genre_filter, Movie.movie_id != movie_id).order_by(func.random()).limit(6).all()
    else:
        similar = db.query(Movie).filter(Movie.movie_id != movie_id).order_by(func.random()).limit(6).all()
        
    return [{"movieId": m.movie_id, "title": m.title, "genres": m.genres} for m in similar]

class WatchlistSchema(BaseModel):
    user_id: int
    movie_id: int

@app.post("/watchlist")
def add_to_watchlist(item: WatchlistSchema, db: Session = Depends(get_db)):
    from backend.database import Watchlist
    # check if already exists
    existing = db.query(Watchlist).filter(Watchlist.user_id == item.user_id, Watchlist.movie_id == item.movie_id).first()
    if not existing:
        new_item = Watchlist(user_id=item.user_id, movie_id=item.movie_id)
        db.add(new_item)
        db.commit()
    return {"status": "success"}

@app.get("/watchlist/{user_id}")
def get_watchlist(user_id: int, db: Session = Depends(get_db)):
    from backend.database import Watchlist, Movie
    items = db.query(Watchlist, Movie).join(Movie, Watchlist.movie_id == Movie.movie_id).filter(Watchlist.user_id == user_id).all()
    return [{"movieId": m.movie_id, "title": m.title, "genres": m.genres, "timestamp": w.timestamp} for w, m in items]
