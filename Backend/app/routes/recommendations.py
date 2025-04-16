'''
This file creates the routes for the recommendations and song retrieval.
'''
from fastapi import APIRouter, HTTPException
from models.song import (
    Song,
    RecommendationRequest,
    RecommendationResponse,
    SongBasedRequest,
    ArtistBasedRequest
)
from services.recommendation_service import RecommendationService

router = APIRouter()
recommendation_service = RecommendationService()

@router.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """Get recommendations based on either a song or an artist"""
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
    try:
        song = await recommendation_service.get_song(song_id)
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        return song
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    