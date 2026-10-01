from sqlalchemy import Column, Integer, Float, DateTime, func, ForeignKey
from backend.database import Base


class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    movie_id = Column(
        Integer, ForeignKey("movies.movie_id"), nullable=False, index=True
    )
    rating = Column(Float, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
