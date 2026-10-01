import sys
import os

# Add parent directory to path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.movie import Movie
from backend.services.metadata_service import fetch_omdb_metadata
from backend.services.image_service import download_and_cache_poster
import time


def run_bootstrap(limit=None):
    db: Session = SessionLocal()

    # Query movies that don't have a poster_url yet
    query = db.query(Movie).filter(Movie.poster_url == None)
    if limit:
        query = query.limit(limit)

    movies = query.all()
    total = len(movies)

    print(f"Starting bootstrap for {total} movies without posters...")

    for i, movie in enumerate(movies):
        print(f"[{i+1}/{total}] Fetching metadata for: {movie.title}")
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
        print(f"  -> No poster found or OMDB error.")
        # Sleep briefly to avoid hammering the OMDB API
        time.sleep(0.1)

    db.close()
    print("Bootstrap complete!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    run_bootstrap(limit=args.limit)
