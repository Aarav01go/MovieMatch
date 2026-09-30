from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import pickle
import os
import google.generativeai as genai
from typing import List
from sqlalchemy.orm import Session
from backend.database import get_db, User, Movie, Rating

app = FastAPI(title="MovieMatch API")

# Setup GenAI
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))

# Load Models
models = {}
for algo in ['svd', 'knn', 'baseline']:
    try:
        with open(f"backend/models/{algo}_model.pkl", "rb") as f:
            models[algo] = pickle.load(f)
    except:
        models[algo] = None

class UserSchema(BaseModel):
    username: str

class RatingSchema(BaseModel):
    user_id: int
    movie_id: int
    rating: float

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
            model = genai.GenerativeModel('gemini-flash-latest')
            prompt = f"Provide details for a real movie matching '{q}'. Format exactly as: Title|Genre1,Genre2. If it is not a real movie, return exactly 'NOT_FOUND'."
            response = model.generate_content(prompt).text.strip()
            if "NOT_FOUND" not in response and "|" in response:
                title, genres = response.split("|", 1)
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
        model = genai.GenerativeModel('gemini-flash-latest')
        res = model.generate_content(f"Write a 2-sentence captivating synopsis for '{title}'.")
        return {"synopsis": res.text}
    except Exception as e:
        return {"synopsis": "Synopsis unavailable."}

@app.post("/ai/rerank")
def rerank_by_mood(req: MoodRequest):
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        titles = ", ".join(req.movies)
        prompt = f"Movies: {titles}. User's mood: '{req.mood}'. Re-order to best match. Return a numbered list."
        res = model.generate_content(prompt)
        return {"result": res.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
