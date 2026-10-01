import gzip
import csv
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.movie import Movie

FILE_PATH = "backend/data/imdb.tsv.gz"


def run():
    db = SessionLocal()
    max_movie = db.query(Movie).order_by(Movie.movie_id.desc()).first()
    max_id = max_movie.movie_id if max_movie else 1
    next_id = max_id + 1000

    print("Streaming IMDB dataset for movies between 2005 and 2026...")

    count = 0
    batch = []

    with gzip.open(FILE_PATH, "rt", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        for row in reader:
            if len(row) < 9:
                continue
            if row[1] != "movie":
                continue

            startYear = row[5]
            if not startYear.isdigit():
                continue
            year = int(startYear)

            # Target the missing years (2005-2009 and 2025-2026) to complete the timeline
            if not ((2005 <= year <= 2009) or (2025 <= year <= 2026)):
                continue

            if row[4] == "1":
                continue  # skip adult

            title = row[2]
            genres = row[8]
            if genres == "\\N":
                genres = "Drama"
            genres = genres.replace(",", "|")

            search_title = f"{title} ({year})"

            # Simple check if already exists to prevent duplicate titles
            # For speed in streaming, we'll just insert everything since movie_id is primary key,
            # but to prevent title duplication we can just rely on the fact that these years were skipped before.

            batch.append(
                Movie(
                    movie_id=next_id, title=search_title, genres=genres, poster_url=None
                )
            )
            next_id += 1
            count += 1

            if len(batch) >= 2000:
                db.bulk_save_objects(batch)
                db.commit()
                print(f"Injected {count} movies so far...")
                batch = []

            if count >= 30000:  # Cap to prevent DB explosion
                break

    if batch:
        db.bulk_save_objects(batch)
        db.commit()

    print(f"SUCCESS: Injected {count} brand new movies (2005-2009 & 2025-2026)!")
    db.close()


if __name__ == "__main__":
    run()
