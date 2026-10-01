import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.movie import Movie
from backend.services.metadata_service import fetch_omdb_metadata
from backend.services.image_service import download_and_cache_poster
import time


def run_bootstrap_modern(limit=1000):
    db: Session = SessionLocal()

    # Query modern movies (2010+) without posters
    query = (
        db.query(Movie)
        .filter(
            (Movie.title.like("%(201%)%") | Movie.title.like("%(202%)%")),
            Movie.poster_url == None,
        )
        .limit(limit)
    )

    movies = query.all()
    total = len(movies)

    print(f"Starting bootstrap for {total} MODERN movies...")

    for i, movie in enumerate(movies):
        print(f"[{i+1}/{total}] Fetching: {movie.title}")
        metadata = fetch_omdb_metadata(movie.title)

        if metadata and metadata.get("Response") == "True":
            poster_remote = metadata.get("Poster")
            if poster_remote and poster_remote != "N/A":
                local_url = download_and_cache_poster(poster_remote, movie.movie_id)
                if local_url:
                    movie.poster_url = local_url
                    db.commit()
                    print(f"  -> Success: {local_url}")
                    continue
        time.sleep(0.05)

    db.close()
    print("Modern Bootstrap complete!")


if __name__ == "__main__":
    run_bootstrap_modern()
