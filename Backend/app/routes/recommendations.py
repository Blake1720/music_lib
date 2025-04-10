'''
This file creates the routes for the recommendations and song retrieval.
'''
from fastapi import APIRouter, HTTPException
from models.song import Song, RecommendationRequest, RecommendationResponse
from services.recommendation_service import RecommendationService

router = APIRouter()
recommendation_service = RecommendationService()

@router.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    try:
        recommendations = await recommendation_service.get_recommendations(
            song_id=request.song_id,
            limit=request.limit,
            include_features=request.include_features
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/songs/{song_id}", response_model=Song)
async def get_song(song_id: str):
    try:
        song = await recommendation_service.get_song(song_id)
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        return song
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    