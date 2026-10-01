import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.movie import Movie
from backend.services.metadata_service import fetch_omdb_metadata
from backend.services.image_service import download_and_cache_poster


def run_bootstrap_massive():
    db = SessionLocal()

    # Process modern movies (with higher movie_ids from our massive dataset injection)
    # Filter for those lacking posters
    query = (
        db.query(Movie)
        .filter(
            Movie.poster_url == None,
            (Movie.title.like("%(201%)%") | Movie.title.like("%(202%)%")),
        )
        .order_by(Movie.movie_id.desc())
    )

    movies = query.all()
    total = len(movies)

    print(f"Starting massive OMDB poster fetcher for {total} new movies...")

    for i, movie in enumerate(movies):
        if i % 100 == 0:
            print(f"[{i}/{total}] Processing...")

        metadata = fetch_omdb_metadata(movie.title)

        if metadata and metadata.get("Response") == "True":
            poster_remote = metadata.get("Poster")
            if poster_remote and poster_remote != "N/A":
                local_url = download_and_cache_poster(poster_remote, movie.movie_id)
                if local_url:
                    movie.poster_url = local_url
                    db.commit()
                    continue

        # Keep OMDB API happy by not spamming too hard
        time.sleep(0.01)

    db.close()
    print("Massive Bootstrap complete!")


if __name__ == "__main__":
    run_bootstrap_massive()
