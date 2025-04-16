'''
This file creates the routes for the recommendations and song retrieval.
'''
from fastapi import APIRouter, HTTPException
from typing import List, Optional
import sqlite3
import os
from app.models.song import (
    Song,
    RecommendationRequest,
    RecommendationResponse,
    SongBasedRequest,
    ArtistBasedRequest
)
from app.services.recommendation_service import RecommendationService

router = APIRouter()

# Initialize recommendation service as None - it will be set by main.py
recommendation_service = None

@router.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """Get recommendations based on either a song or an artist"""
    if not recommendation_service:
        raise HTTPException(status_code=503, detail="Recommendation service not initialized")

    try:
        if isinstance(request.request, SongBasedRequest):
            recommendations = await recommendation_service.get_recommendations_by_song(
                song_id=request.request.song_id,
                limit=request.request.limit
            )
        else:  # ArtistBasedRequest
            recommendations = await recommendation_service.get_recommendations_by_artist(
                artist_id=request.request.artist_id,
                limit=request.request.limit
            )
        return recommendations
    except ValueError as e:
        # For known errors like "Song not found" or "No songs found for artist"
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # For unexpected errors
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/songs/{song_id}", response_model=Song)
async def get_song(song_id: str):
    """Get a specific song by ID"""
    if not recommendation_service:
        raise HTTPException(status_code=503, detail="Recommendation service not initialized")

    try:
        song = await recommendation_service.get_song(song_id)
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        return song
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/song/{song_id}")
async def get_song_recommendations(song_id: str, limit: Optional[int] = 10) -> RecommendationResponse:
    """Get recommendations based on a specific song"""
    if not recommendation_service:
        raise HTTPException(status_code=503, detail="Recommendation service not initialized")
    
    try:
        result = await recommendation_service.get_recommendations_by_song(song_id, limit)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/artist/{artist_id}")
async def get_artist_recommendations(artist_id: int, limit: Optional[int] = 10) -> RecommendationResponse:
    """Get recommendations based on an artist's style"""
    if not recommendation_service:
        raise HTTPException(status_code=503, detail="Recommendation service not initialized")
    
    try:
        result = await recommendation_service.get_recommendations_by_artist(artist_id, limit)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    