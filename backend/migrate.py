import pandas as pd
from database import SessionLocal, Movie, engine, Base
from sqlalchemy import text

def migrate():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if movies exist
    if db.query(Movie).first() is None:
        print("Migrating movies.csv to SQL Database...")
        try:
            movies_df = pd.read_csv("backend/data/movies.csv")
            movies_to_insert = [
                Movie(movie_id=row['movieId'], title=row['title'], genres=row['genres'])
                for _, row in movies_df.iterrows()
            ]
            db.bulk_save_objects(movies_to_insert)
            db.commit()
            print(f"Successfully inserted {len(movies_to_insert)} movies into the database.")
        except Exception as e:
            print(f"Error migrating movies: {e}")
            db.rollback()
    else:
        print("Movies table already populated.")
        
    db.close()

if __name__ == "__main__":
    migrate()
