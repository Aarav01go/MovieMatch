import re
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.movie import Movie


def clean_title(title):
    original = title

    # 1. Remove (a.k.a. ...)
    title = re.sub(r"\(a\.k\.a\.[^)]+\)", "", title)

    # 2. Fix ", The", ", A", ", An" before the year
    # E.g., "Matrix, The (1999)" -> "The Matrix (1999)"
    # Matches (..., The ) followed by (YYYY)
    match = re.search(r", (The|A|An)\s*(\(\d{4}\))?$", title, re.IGNORECASE)
    if match:
        article = match.group(1)
        year_part = match.group(2) if match.group(2) else ""
        # Remove the ", Article" part
        title = re.sub(
            r", (The|A|An)\s*(\(\d{4}\))?$", f"{year_part}", title, flags=re.IGNORECASE
        )
        # Prepend the article
        title = f"{article} {title.strip()}"

    # Same thing but if the year is guaranteed at the end:
    # "American President, The (1995)"
    match2 = re.search(r"(.*?), (The|A|An)\s*(\(\d{4}\))?$", title, re.IGNORECASE)
    if match2:
        base = match2.group(1).strip()
        article = match2.group(2).strip()
        year = match2.group(3).strip() if match2.group(3) else ""
        title = f"{article} {base} {year}"

    # 3. Remove alternate language titles in parentheses right before the year
    # E.g., "City of Lost Children (Cité des enfants perdus, La) (1995)" -> "City of Lost Children (1995)"
    title = re.sub(r"\s*\([^)]*[a-zA-Z]+[^)]*\)\s*(\(\d{4}\))$", r" \1", title)

    # 4. Clean up multiple spaces
    title = re.sub(r"\s+", " ", title).strip()

    return title


def run():
    db = SessionLocal()
    movies = db.query(Movie).all()
    count = 0

    print("Scanning database for messy titles...")

    for m in movies:
        cleaned = clean_title(m.title)
        if cleaned != m.title:
            # print(f"Fixing: {m.title} -> {cleaned}")
            m.title = cleaned
            count += 1

        if count > 0 and count % 5000 == 0:
            db.commit()

    db.commit()
    print(f"Successfully cleaned and corrected {count} movie titles!")
    db.close()


if __name__ == "__main__":
    run()
