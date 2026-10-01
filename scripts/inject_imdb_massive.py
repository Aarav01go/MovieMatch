import gzip
import csv
import os
import sys

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

    print("Streaming IMDB dataset and injecting modern movies (2010-2024)...")

    count = 0
    batch = []

    with gzip.open(FILE_PATH, "rt", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)  # skip header
        for row in reader:
            if len(row) < 9:
                continue
            titleType = row[1]
            if titleType != "movie":
                continue

            startYear = row[5]
            if not startYear.isdigit():
                continue
            year = int(startYear)
            if year < 2010 or year > 2024:
                continue

            isAdult = row[4]
            if isAdult == "1":
                continue

            title = row[2]
            genres = row[8]
            if genres == "\\N":
                genres = "Drama"
            genres = genres.replace(",", "|")

            search_title = f"{title} ({year})"

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

            # Cap at 50,000 recent movies to keep SQLite perfectly optimized
            if count >= 50000:
                break

    if batch:
        db.bulk_save_objects(batch)
        db.commit()

    print(f"SUCCESS: Injected {count} brand new modern movies into the dataset!")
    db.close()


if __name__ == "__main__":
    run()
