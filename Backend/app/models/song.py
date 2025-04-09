from pydantic import BaseModel
from typing import List, Optional

class Song(BaseModel):
    id: str
    title: str
    artist: str
    album: Optional[str] = None
    genre: List[str] = []
    duration: int  # in seconds
    popularity: float  # 0.0 to 1.0
    features: Optional[dict] = None  # For audio features like tempo, energy, etc.

class RecommendationRequest(BaseModel):
    song_id: str
    limit: int = 10
    include_features: bool = False

class RecommendationResponse(BaseModel):
    recommendations: List[Song]
    metadata: dict 