'''
This file creates the routes for importing songs from Spotify.
'''
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

# Initialize router
router = APIRouter()

# Initialize service (will be set by main.py)
spotify_service = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpotifyImportRequest(BaseModel):
    spotify_url: str
    user_id: Optional[str] = None

class SpotifyImportResponse(BaseModel):
    success: bool
    message: str
    song_id: Optional[str] = None

@router.post("/import", response_model=SpotifyImportResponse)
async def import_spotify_song(request: SpotifyImportRequest):
    if not spotify_service:
        raise HTTPException(status_code=500, detail="Spotify service not initialized")
    
    try:
        logger.info(f"Importing song from Spotify URL: {request.spotify_url}")
        song_id = spotify_service.import_song(request.spotify_url, request.user_id)
        return SpotifyImportResponse(
            success=True,
            message="Song imported successfully",
            song_id=song_id
        )
    except Exception as e:
        logger.error(f"Error importing song: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e)) 