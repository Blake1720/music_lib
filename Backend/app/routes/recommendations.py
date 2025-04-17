'''
This file creates the routes for the recommendations and song retrieval.
'''
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import random
import os
from typing import Dict, Any
from datetime import datetime
from app.models.song import (
    Song,
    RecommendationRequest,
    RecommendationResponse,
    SongBasedRequest,
    ArtistBasedRequest
)
from app.services.recommendation_service import RecommendationService

router = APIRouter()

# Models

class GenerateSongPlaylistRequest(BaseModel):
    song_id: str
    username: str
    name: str
    limit: Optional[int] = 10

class GenerateArtistPlaylistRequest(BaseModel):
    artist_name: str
    username: str
    name: str
    limit: Optional[int] = 10

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

@router.post("/songs/generate")
async def make_song_recommendations(
    request: GenerateSongPlaylistRequest
):
    """Get recommendations based on a specific song and generate a playlist"""
    song_id = request.song_id
    username = request.username
    name = request.name
    limit = request.limit

    if not recommendation_service:
        raise HTTPException(status_code=503, detail="Recommendation service not initialized")
    
    try:
        recommendations_response = await recommendation_service.get_recommendations_by_song(song_id, limit=limit)
        base_song = await recommendation_service.get_song(song_id)

        if not base_song:
            raise ValueError("Base song not found")

        songs = [base_song] + recommendations_response.recommendations

        # Connect to DB
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(root_dir, "../Database/music_app.db")
        conn = sqlite3.connect(db_path)

        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM User WHERE name = ?", (username,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("Username not found")
        
        user_id = row[0]

        try:
            # Insert playlist
            cursor.execute("""
                INSERT INTO Playlist (user_id, name, date_created)
                VALUES (?, ?, ?)
            """, (user_id, name, datetime.now()))

            # Insert songs into playlist
            for song in songs:
                cursor.execute("""
                    INSERT INTO Playlist_Song (user_id, playlist_name, song_id)
                    VALUES (?, ?, ?)
                """, (user_id, name, song.id))
            
            conn.commit()

        except sqlite3.IntegrityError as e:
            raise ValueError(f"Failed to store playlist: {str(e)}")

        finally:
            conn.close()

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "playlist": {
            "name": name,
            "user_id": user_id,
            "base_song": base_song.title,
            "songs": [song.title for song in songs],
            "created_at": str(datetime.now())
        }
    }

@router.post("/artists/generate")
async def make_artist_recommendations(request: GenerateArtistPlaylistRequest):
    print("Incoming request:", request)

    if not recommendation_service:
        print("Recommendation service not initialized")
        raise HTTPException(status_code=503, detail="Recommendation service not initialized")

    try:
        # Connect to DB
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(root_dir, "../Database/music_app.db")
        playlist_name = f"{request.name} #{random.randint(1000, 9999)}"
        print("Connecting to DB:", db_path)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get artist_id
        print("Looking up artist:", request.artist_name)
        cursor.execute("SELECT artist_id FROM Artist WHERE name = ?", (request.artist_name,))
        artist_row = cursor.fetchone()
        if not artist_row:
            print("Artist not found:", request.artist_name)
            raise ValueError("Artist not found")
        artist_id = artist_row[0]
        print("Artist ID:", artist_id)

        # Get user_id
        print("Looking up user:", request.username)
        cursor.execute("SELECT user_id FROM User WHERE name = ?", (request.username,))
        user_row = cursor.fetchone()
        if not user_row:
            print("User not found:", request.username)
            raise ValueError("Username not found")
        user_id = user_row[0]
        print("User ID:", user_id)

        # Get recommendations
        print("Getting recommendations...")
        recommendations_response = await recommendation_service.get_recommendations_by_artist(artist_id, limit=request.limit)
        songs = recommendations_response.recommendations
        print(f"Got {len(songs)} recommendations")

        # Store playlist
        print("Inserting playlist...")
        cursor.execute("""
            INSERT INTO Playlist (user_id, name, date_created)
            VALUES (?, ?, ?)
        """, (user_id, request.name, datetime.now()))

        for song in songs:
            cursor.execute("""
                INSERT INTO Playlist_Song (user_id, playlist_name, song_id)
                VALUES (?, ?, ?)
            """, (user_id, request.name, song.id))

        conn.commit()
        print("Playlist inserted successfully.")

    except sqlite3.IntegrityError as e:
        print("SQL IntegrityError:", e)
        raise HTTPException(status_code=400, detail=f"Playlist insert error: {str(e)}")
    except ValueError as e:
        print("ValueError:", e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print("Unhandled Exception:", e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

    return {
        "playlist": {
            "name": request.name,
            "user_id": user_id,
            "songs": [song.title for song in songs],
            "created_at": str(datetime.now())
        }
    }