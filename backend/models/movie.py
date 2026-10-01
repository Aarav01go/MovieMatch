from sqlalchemy import Column, Integer, String
from backend.database import Base


class Movie(Base):
    __tablename__ = "movies"
    movie_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    genres = Column(String)
    poster_url = Column(String, nullable=True)
    backdrop_url = Column(String, nullable=True)
