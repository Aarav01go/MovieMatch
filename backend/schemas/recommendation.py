from pydantic import BaseModel
from typing import List


class MoodRequest(BaseModel):
    movies: List[str]
    mood: str
