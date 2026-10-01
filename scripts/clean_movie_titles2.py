import re
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.movie import Movie


def clean_title2(title):
    original = title

    # 1. Fix missing space before year parenthesis: "Movie(2000)" -> "Movie (2000)"
    title = re.sub(r"(?<!\s)(\(\d{4}\))$", r" \1", title)

    # 2. Fix ", The" if it survived
    match = re.search(r"(.*?), (The|A|An)\s*(\(\d{4}\))?$", title, re.IGNORECASE)
    if match:
        base = match.group(1).strip()
        article = match.group(2).strip()
        year = match.group(3).strip() if match.group(3) else ""
        title = f"{article} {base} {year}"

    title = re.sub(r"\s+", " ", title).strip()
    return title


def run():
    db = SessionLocal()
    movies = db.query(Movie).all()
    count = 0

    for m in movies:
        cleaned = clean_title2(m.title)
        if cleaned != m.title:
            m.title = cleaned
            count += 1

    db.commit()
    print(f"Second pass: Cleaned {count} movie titles!")
    db.close()


if __name__ == "__main__":
    run()
