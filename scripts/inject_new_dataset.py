import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.movie import Movie
from backend.services.metadata_service import fetch_omdb_metadata
from backend.services.image_service import download_and_cache_poster

modern_movies = [
    {"title": "Inception", "year": "2010"},
    {"title": "The Social Network", "year": "2010"},
    {"title": "Black Swan", "year": "2010"},
    {"title": "Toy Story 3", "year": "2010"},
    {"title": "Drive", "year": "2011"},
    {"title": "Harry Potter and the Deathly Hallows: Part 2", "year": "2011"},
    {"title": "The Avengers", "year": "2012"},
    {"title": "Django Unchained", "year": "2012"},
    {"title": "The Dark Knight Rises", "year": "2012"},
    {"title": "The Wolf of Wall Street", "year": "2013"},
    {"title": "Gravity", "year": "2013"},
    {"title": "12 Years a Slave", "year": "2013"},
    {"title": "Interstellar", "year": "2014"},
    {"title": "Whiplash", "year": "2014"},
    {"title": "Gone Girl", "year": "2014"},
    {"title": "John Wick", "year": "2014"},
    {"title": "Guardians of the Galaxy", "year": "2014"},
    {"title": "Mad Max: Fury Road", "year": "2015"},
    {"title": "The Martian", "year": "2015"},
    {"title": "Inside Out", "year": "2015"},
    {"title": "Star Wars: Episode VII - The Force Awakens", "year": "2015"},
    {"title": "Arrival", "year": "2016"},
    {"title": "La La Land", "year": "2016"},
    {"title": "Moonlight", "year": "2016"},
    {"title": "Deadpool", "year": "2016"},
    {"title": "Get Out", "year": "2017"},
    {"title": "Blade Runner 2049", "year": "2017"},
    {"title": "Logan", "year": "2017"},
    {"title": "Dunkirk", "year": "2017"},
    {"title": "Spider-Man: Into the Spider-Verse", "year": "2018"},
    {"title": "Avengers: Infinity War", "year": "2018"},
    {"title": "Black Panther", "year": "2018"},
    {"title": "Parasite", "year": "2019"},
    {"title": "Joker", "year": "2019"},
    {"title": "Avengers: Endgame", "year": "2019"},
    {"title": "Knives Out", "year": "2019"},
    {"title": "1917", "year": "2019"},
    {"title": "Tenet", "year": "2020"},
    {"title": "Soul", "year": "2020"},
    {"title": "Dune", "year": "2021"},
    {"title": "Spider-Man: No Way Home", "year": "2021"},
    {"title": "The Batman", "year": "2022"},
    {"title": "Top Gun: Maverick", "year": "2022"},
    {"title": "Everything Everywhere All at Once", "year": "2022"},
    {"title": "Avatar: The Way of Water", "year": "2022"},
    {"title": "Oppenheimer", "year": "2023"},
    {"title": "Barbie", "year": "2023"},
    {"title": "Spider-Man: Across the Spider-Verse", "year": "2023"},
    {"title": "Guardians of the Galaxy Vol. 3", "year": "2023"},
    {"title": "Dune: Part Two", "year": "2024"},
    {"title": "Furiosa: A Mad Max Saga", "year": "2024"},
    {"title": "Deadpool & Wolverine", "year": "2024"},
    {"title": "Inside Out 2", "year": "2024"},
]


def inject_movies():
    db = SessionLocal()

    print(
        f"Injecting {len(modern_movies)} brand new modern movies into the database..."
    )

    added_count = 0
    max_id = db.query(Movie).order_by(Movie.movie_id.desc()).first().movie_id
    next_id = max_id + 1000

    for item in modern_movies:
        title = item.get("title")
        year = item.get("year")
        search_title = f"{title} ({year})"

        # Check if it already exists
        exists = db.query(Movie).filter(Movie.title.ilike(f"%{title}%")).first()
        if exists:
            print(f"Skipping {title} (Already in DB)")
            continue

        print(f"Adding new movie: {search_title}")

        metadata = fetch_omdb_metadata(title)
        genres = "Action|Drama"  # default
        poster_url = None

        if metadata and metadata.get("Response") == "True":
            genres_raw = metadata.get("Genre", "Action|Drama")
            genres = genres_raw.replace(", ", "|")

            poster_remote = metadata.get("Poster")
            if poster_remote and poster_remote != "N/A":
                poster_url = download_and_cache_poster(poster_remote, next_id)

        new_movie = Movie(
            movie_id=next_id, title=search_title, genres=genres, poster_url=poster_url
        )
        db.add(new_movie)
        db.commit()
        added_count += 1
        next_id += 1
        time.sleep(0.1)

    print(
        f"Successfully injected {added_count} brand new modern movies into the dataset!"
    )
    db.close()


if __name__ == "__main__":
    inject_movies()
