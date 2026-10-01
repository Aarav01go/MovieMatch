import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.movie import Movie
from backend.services.metadata_service import fetch_omdb_metadata
from backend.services.image_service import download_and_cache_poster

marvel_movies = [
    ("Iron Man", 2008),
    ("The Incredible Hulk", 2008),
    ("Iron Man 2", 2010),
    ("Thor", 2011),
    ("Captain America: The First Avenger", 2011),
    ("The Avengers", 2012),
    ("Iron Man 3", 2013),
    ("Thor: The Dark World", 2013),
    ("Captain America: The Winter Soldier", 2014),
    ("Guardians of the Galaxy", 2014),
    ("Avengers: Age of Ultron", 2015),
    ("Ant-Man", 2015),
    ("Captain America: Civil War", 2016),
    ("Doctor Strange", 2016),
    ("Guardians of the Galaxy Vol. 2", 2017),
    ("Spider-Man: Homecoming", 2017),
    ("Thor: Ragnarok", 2017),
    ("Black Panther", 2018),
    ("Avengers: Infinity War", 2018),
    ("Ant-Man and the Wasp", 2018),
    ("Captain Marvel", 2019),
    ("Avengers: Endgame", 2019),
    ("Spider-Man: Far From Home", 2019),
    ("Black Widow", 2021),
    ("Shang-Chi and the Legend of the Ten Rings", 2021),
    ("Eternals", 2021),
    ("Spider-Man: No Way Home", 2021),
    ("Doctor Strange in the Multiverse of Madness", 2022),
    ("Thor: Love and Thunder", 2022),
    ("Black Panther: Wakanda Forever", 2022),
    ("Ant-Man and the Wasp: Quantumania", 2023),
    ("Guardians of the Galaxy Vol. 3", 2023),
    ("The Marvels", 2023),
    ("Deadpool & Wolverine", 2024),
]

bollywood_hits = [
    ("Dangal", 2016),
    ("Pathaan", 2023),
    ("Jawan", 2023),
    ("Animal", 2023),
    ("PK", 2014),
    ("Bajrangi Bhaijaan", 2015),
    ("Sanju", 2018),
    ("Sultan", 2016),
    ("Tiger Zinda Hai", 2017),
    ("Padmaavat", 2018),
    ("Dhoom 3", 2013),
    ("War", 2019),
    ("3 Idiots", 2009),
    ("Chennai Express", 2013),
    ("Kick", 2014),
    ("Krrish 3", 2013),
    ("Yeh Jawaani Hai Deewani", 2013),
    ("Lagaan", 2001),
    ("Sholay", 1975),
    ("Dilwale Dulhania Le Jayenge", 1995),
    ("Kabhi Khushi Kabhie Gham", 2001),
    ("Kuch Kuch Hota Hai", 1998),
    ("My Name Is Khan", 2010),
    ("Chak De! India", 2007),
    ("Drishyam", 2015),
    ("Gully Boy", 2019),
    ("Kabir Singh", 2019),
    ("Brahmastra", 2022),
]

tollywood_pan_india_hits = [
    ("Baahubali: The Beginning", 2015),
    ("Baahubali 2: The Conclusion", 2017),
    ("RRR", 2022),
    ("Pushpa: The Rise", 2021),
    ("Salaar: Part 1 - Ceasefire", 2023),
    ("Kalki 2898 AD", 2024),
    ("Ala Vaikunthapurramuloo", 2020),
    ("Eega", 2012),
    ("Magadheera", 2009),
    ("Rangasthalam", 2018),
    ("Arjun Reddy", 2017),
    ("Mahanati", 2018),
    ("Kantara", 2022),
    ("KGF: Chapter 1", 2018),
    ("KGF: Chapter 2", 2022),
    ("Vikram", 2022),
    ("Jailer", 2023),
    ("Leo", 2023),
]


def inject_curated():
    db = SessionLocal()
    all_movies = marvel_movies + bollywood_hits + tollywood_pan_india_hits

    print(f"Injecting {len(all_movies)} curated global hits into the dataset...")

    added_count = 0
    max_id = db.query(Movie).order_by(Movie.movie_id.desc()).first().movie_id
    next_id = max_id + 1000

    for title, year in all_movies:
        search_title = f"{title} ({year})"
        exists = db.query(Movie).filter(Movie.title.ilike(f"%{title}%")).first()
        if exists:
            # Let's actively fetch OMDB poster for it if it's missing, to guarantee it looks perfect!
            if not exists.poster_url:
                metadata = fetch_omdb_metadata(title)
                if metadata and metadata.get("Response") == "True":
                    poster = metadata.get("Poster")
                    if poster and poster != "N/A":
                        exists.poster_url = download_and_cache_poster(
                            poster, exists.movie_id
                        )
                        db.commit()
            print(f"Skipping {title} (Already in DB, poster verified)")
            continue

        print(f"Adding new blockbuster: {search_title}")

        metadata = fetch_omdb_metadata(title)
        genres = "Action|Drama"
        poster_url = None

        if metadata and metadata.get("Response") == "True":
            genres = metadata.get("Genre", "Action|Drama").replace(", ", "|")
            poster = metadata.get("Poster")
            if poster and poster != "N/A":
                poster_url = download_and_cache_poster(poster, next_id)

        new_movie = Movie(
            movie_id=next_id, title=search_title, genres=genres, poster_url=poster_url
        )
        db.add(new_movie)
        db.commit()
        added_count += 1
        next_id += 1
        time.sleep(0.1)

    print(f"Successfully injected {added_count} curated blockbusters!")
    db.close()


if __name__ == "__main__":
    inject_curated()
