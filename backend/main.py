from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import pickle
import sqlite3
import os
import google.generativeai as genai
from typing import List, Optional

app = FastAPI(title="MovieMatch API")

# Setup GenAI
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))

# Load Data
try:
    movies_df = pd.read_csv("backend/data/movies.csv")
except:
    movies_df = pd.DataFrame(columns=['movieId', 'title', 'genres'])

# Load Models
models = {}
for algo in ['svd', 'knn', 'baseline']:
    try:
        with open(f"backend/models/{algo}_model.pkl", "rb") as f:
            models[algo] = pickle.load(f)
    except:
        models[algo] = None

# DB Connection
DB_PATH = "backend/data/moviematch.db"
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class User(BaseModel):
    username: str

class Rating(BaseModel):
    user_id: int
    movie_id: int
    rating: float

class MoodRequest(BaseModel):
    movies: List[str]
    mood: str

@app.post("/users")
def get_or_create_user(user: User):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE username = ?", (user.username,))
    row = cursor.fetchone()
    if row:
        user_id = row['user_id']
    else:
        cursor.execute("INSERT INTO users (username) VALUES (?)", (user.username,))
        conn.commit()
        user_id = cursor.lastrowid
    conn.close()
    return {"user_id": user_id, "username": user.username}

@app.get("/movies/search")
def search_movies(q: str):
    global movies_df
    results = movies_df[movies_df['title'].str.contains(q, case=False, na=False)].head(12)
    if results.empty:
        try:
            model = genai.GenerativeModel('gemini-flash-latest')
            prompt = f"Provide details for a real movie matching '{q}'. Format exactly as: Title|Genre1,Genre2. If it is not a real movie, return exactly 'NOT_FOUND'."
            response = model.generate_content(prompt).text.strip()
            if "NOT_FOUND" not in response and "|" in response:
                title, genres = response.split("|", 1)
                title, genres = title.strip(), genres.strip()
                
                # Check if this exact title actually exists to avoid duplicates
                exact_match = movies_df[movies_df['title'].str.lower() == title.lower()]
                if not exact_match.empty:
                    return exact_match.to_dict(orient="records")
                    
                # Create a new fake ID
                new_id = movies_df['movieId'].max() + 1 if not movies_df.empty else 1
                new_row = {"movieId": int(new_id), "title": title, "genres": genres}
                
                # Append to memory dataframe
                movies_df = pd.concat([movies_df, pd.DataFrame([new_row])], ignore_index=True)
                
                # Persist to CSV so ratings join works across restarts
                movies_df.to_csv("backend/data/movies.csv", index=False)
                
                return [new_row]
        except Exception:
            pass
            
    return results.to_dict(orient="records")

@app.get("/movies/trending")
def trending_movies():
    results = movies_df.sample(6, random_state=42)
    return results.to_dict(orient="records")

@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: int, algo: str = "svd"):
    if algo not in models or models[algo] is None:
        raise HTTPException(status_code=400, detail="Model not found or not trained")
    
    model = models[algo]
    sample = movies_df.sample(200, random_state=42)
    predictions = []
    for _, row in sample.iterrows():
        pred = model.predict(uid=user_id, iid=row['movieId'])
        predictions.append({
            "movieId": row['movieId'],
            "title": row['title'],
            "genres": row['genres'],
            "rating": pred.est
        })
    
    predictions.sort(key=lambda x: x['rating'], reverse=True)
    return predictions[:12]

@app.post("/ratings")
def add_rating(rating: Rating):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ratings (user_id, movie_id, rating) VALUES (?, ?, ?)", 
                  (rating.user_id, rating.movie_id, rating.rating))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.get("/ratings/{user_id}")
def get_ratings(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id, rating, timestamp FROM ratings WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows: return []
    
    ratings_df = pd.DataFrame([dict(r) for r in rows])
    merged = pd.merge(ratings_df, movies_df, left_on='movie_id', right_on='movieId', how='left')
    return merged.to_dict(orient="records")

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
