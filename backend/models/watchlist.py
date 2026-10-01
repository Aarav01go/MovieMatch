from sqlalchemy import Column, Integer, DateTime, func, ForeignKey
from backend.database import Base


class Watchlist(Base):
    __tablename__ = "watchlist"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    movie_id = Column(
        Integer, ForeignKey("movies.movie_id"), nullable=False, index=True
    )
    timestamp = Column(DateTime, server_default=func.now())
