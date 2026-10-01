import re
import requests
from backend.config import settings


def call_openrouter(prompt: str) -> str:
    if not settings.OPENROUTER_KEY:
        return "AI Service Unavailable (No API Key)"
    try:
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "google/gemini-2.5-flash",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
        }
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"AI Service temporarily unavailable. {e}"


def generate_synopsis(title: str) -> str:
    return call_openrouter(
        f"Write a 2-sentence captivating cinematic synopsis for the movie '{title}'."
    )


def rerank_movies_by_mood(movies: list, mood: str) -> str:
    prompt = f"Here are some movies: {', '.join(movies)}. The user is in the mood for: '{mood}'. Re-order these movies to best match this mood. Return ONLY a numbered list."
    return call_openrouter(prompt)


from sqlalchemy.orm import Session
from backend.models.movie import Movie


def get_ai_recommendation(query: str, db: Session):
    prompt = f"The user says: '{query}'. Suggest exactly ONE movie that best fits this. Return EXACTLY in this format: TITLE: [Movie Title] | REASON: [Brief 1-sentence reason]"
    raw_response = call_openrouter(prompt)

    try:
        parts = raw_response.split("|")
        title_part = (
            [p for p in parts if "TITLE:" in p][0].replace("TITLE:", "").strip()
        )
        reason_part = (
            [p for p in parts if "REASON:" in p][0].replace("REASON:", "").strip()
        )

        # Strip years and quotes from title just in case
        clean_title = re.sub(r"\(.*?\)", "", title_part).strip(" \"'")

        # Find in DB
        movie = db.query(Movie).filter(Movie.title.ilike(f"%{clean_title}%")).first()

        if movie:
            return {
                "success": True,
                "message": reason_part,
                "movie": {
                    "movieId": movie.movie_id,
                    "title": movie.title,
                    "poster_url": movie.poster_url,
                },
            }
        else:
            return {
                "success": True,
                "message": f"I recommend {title_part}! {reason_part} (Search for it in the Discover tab to add it to our database!)",
                "movie": None,
            }
    except Exception as e:
        return {
            "success": False,
            "message": "I'm having trouble thinking of a movie right now. "
            + raw_response,
            "movie": None,
        }
