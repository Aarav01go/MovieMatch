from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.sql.expression import func
from backend.models.movie import Movie
from backend.services.ai_service import call_openrouter


def get_trending(db: Session, limit: int = 12):
    return (
        db.query(Movie)
        .filter(Movie.poster_url != None)
        .order_by(func.random())
        .limit(limit)
        .all()
    )


def search_movies(q: str, db: Session):
    results = (
        db.query(Movie)
        .filter(Movie.title.ilike(f"%{q}%"), Movie.poster_url != None)
        .limit(12)
        .all()
    )
    if not results:
        results = db.query(Movie).filter(Movie.title.ilike(f"%{q}%")).limit(12).all()
    if not results:
        prompt = f"Provide details for a real movie matching '{q}'. Format exactly as: Title|Genre1,Genre2. If not real, return 'NOT_FOUND'."
        response_text = call_openrouter(prompt)
        if "NOT_FOUND" not in response_text and "|" in response_text:
            try:
                title, genres = response_text.split("|", 1)
                title, genres = title.strip(), genres.strip()
                exact = db.query(Movie).filter(Movie.title.ilike(title)).first()
                if exact:
                    return [exact]

                max_id = db.query(Movie).order_by(Movie.movie_id.desc()).first()
                new_id = (max_id.movie_id + 1) if max_id else 1
                new_movie = Movie(movie_id=new_id, title=title, genres=genres)
                db.add(new_movie)
                db.commit()
                db.refresh(new_movie)
                return [new_movie]
            except:
                pass
    return results


def get_by_id(movie_id: int, db: Session):
    return db.query(Movie).filter(Movie.movie_id == movie_id).first()


def get_similar(movie_id: int, db: Session, limit: int = 6):
    movie = get_by_id(movie_id, db)
    if not movie:
        return []
    genres = movie.genres.split("|") if movie.genres else []
    if genres:
        genre_filter = or_(*[Movie.genres.ilike(f"%{g.strip()}%") for g in genres])
        return (
            db.query(Movie)
            .filter(genre_filter, Movie.movie_id != movie_id, Movie.poster_url != None)
            .order_by(func.random())
            .limit(limit)
            .all()
        )
    return (
        db.query(Movie)
        .filter(Movie.movie_id != movie_id, Movie.poster_url != None)
        .order_by(func.random())
        .limit(limit)
        .all()
    )


def get_recent_movies(db: Session, limit: int = 15):
    # Match movies with (201x) or (202x) in the title and have a poster
    results = (
        db.query(Movie)
        .filter(
            (Movie.title.like("%(201%)%") | Movie.title.like("%(202%)%")),
            Movie.poster_url != None,
        )
        .order_by(func.random())
        .limit(limit)
        .all()
    )

    if len(results) < limit:
        # Fallback if not enough have posters yet
        more = (
            db.query(Movie)
            .filter((Movie.title.like("%(201%)%") | Movie.title.like("%(202%)%")))
            .limit(limit - len(results))
            .all()
        )
        results.extend(more)

    return results


import re


def get_sequels(movie_id: int, db: Session, limit: int = 10):
    movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
    if not movie:
        return []

    title = movie.title
    title = re.sub(r"\(\d{4}\)", "", title).strip()
    title = re.split(r"[:\-]", title)[0].strip()
    title = re.sub(r"\s+\d+$", "", title).strip()
    title = re.sub(
        r"\s+(I|II|III|IV|V|VI|VII|VIII|IX|X)$", "", title, flags=re.IGNORECASE
    ).strip()

    if len(title) < 3:
        return []

    results = (
        db.query(Movie)
        .filter(
            Movie.title.ilike(f"{title}%"),
            Movie.movie_id != movie_id,
            Movie.poster_url != None,
        )
        .order_by(Movie.title)
        .limit(limit)
        .all()
    )

    # If no poster found, fallback to anything
    if not results:
        results = (
            db.query(Movie)
            .filter(Movie.title.ilike(f"{title}%"), Movie.movie_id != movie_id)
            .order_by(Movie.title)
            .limit(limit)
            .all()
        )

    return results


def get_marvel_movies(db: Session, limit: int = 15):
    return (
        db.query(Movie)
        .filter(
            (
                Movie.title.ilike("%Iron Man%")
                | Movie.title.ilike("%Captain America%")
                | Movie.title.ilike("%Avengers%")
                | Movie.title.ilike("%Thor%")
                | Movie.title.ilike("%Guardians of the Galaxy%")
                | Movie.title.ilike("%Black Panther%")
                | Movie.title.ilike("%Ant-Man%")
                | Movie.title.ilike("%Spider-Man%")
            ),
            Movie.poster_url != None,
        )
        .order_by(func.random())
        .limit(limit)
        .all()
    )


def get_bollywood_tollywood(db: Session, limit: int = 15):
    # Some hardcoded iconic keywords to pull from the DB
    return (
        db.query(Movie)
        .filter(
            (
                Movie.title.ilike("%Dangal%")
                | Movie.title.ilike("%Pathaan%")
                | Movie.title.ilike("%Jawan%")
                | Movie.title.ilike("%Baahubali%")
                | Movie.title.ilike("%RRR%")
                | Movie.title.ilike("%Pushpa%")
                | Movie.title.ilike("%KGF%")
                | Movie.title.ilike("%Salaar%")
                | Movie.title.ilike("%Kalki%")
                | Movie.title.ilike("%3 Idiots%")
                | Movie.title.ilike("%Lagaan%")
                | Movie.title.ilike("%Sholay%")
            ),
            Movie.poster_url != None,
        )
        .order_by(func.random())
        .limit(limit)
        .all()
    )
