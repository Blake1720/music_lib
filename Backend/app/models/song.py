'''
This file defines the models for the songs and recommendations.
'''
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal

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

class SongBasedRequest(BaseModel):
    """Request for song-based recommendations"""
    type: Literal["song"] = "song"
    song_id: str
    limit: int = Field(default=10, ge=1, le=50)

class ArtistBasedRequest(BaseModel):
    """Request for artist-based recommendations"""
    type: Literal["artist"] = "artist"
    artist_id: int
    limit: int = Field(default=10, ge=1, le=50)

class RecommendationRequest(BaseModel):
    """Union type that accepts either song-based or artist-based recommendation requests"""
    request: Union[SongBasedRequest, ArtistBasedRequest]

class RecommendationResponse(BaseModel):
    recommendations: List[Song]
    metadata: dict 