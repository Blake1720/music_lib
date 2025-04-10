from pydantic import BaseModel
from typing import List, Optional

class Song(BaseModel):
    id: str
    title: str
    artist: str
    album: str
    genre: List[str]
    duration: float
    tempo: float
    spectral_centroid: float
    spectral_rolloff: float
    spectral_contrast: float
    chroma_mean: float
    chroma_std: float
    harmonic_ratio: float
    onset_strength: float
    zero_crossing_rate: float
    rms_energy: float

class RecommendationRequest(BaseModel):
    song_id: str
    limit: int = 10
    include_features: bool = False

class RecommendationResponse(BaseModel):
    recommendations: List[Song]
    metadata: dict 