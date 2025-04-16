'''
This file creates the routes for the database.
'''
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import sqlite3
import os
from app.services.propagateDB import fetch_and_store_songs
from app.services.display_database import (
    display_all_artists,
    display_all_albums,
    display_all_songs,
    display_database_summary
)

router = APIRouter()

# Response Models
class SongResponse(BaseModel):
    id: str
    name: str
    artist: str
    album: str
    genre: Optional[str] = None
    duration: Optional[float] = None
    tempo: Optional[float] = None
    spectral_centroid: Optional[float] = None
    spectral_rolloff: Optional[float] = None
    spectral_contrast: Optional[float] = None
    chroma_mean: Optional[float] = None
    chroma_std: Optional[float] = None
    onset_strength: Optional[float] = None
    zero_crossing_rate: Optional[float] = None
    rms_energy: Optional[float] = None

class SongsResponse(BaseModel):
    songs: List[SongResponse]

class ArtistResponse(BaseModel):
    id: str
    name: str
    album_count: Optional[int] = None
    song_count: Optional[int] = None

class ArtistsResponse(BaseModel):
    artists: List[ArtistResponse]

class AlbumResponse(BaseModel):
    id: str
    name: str
    artist: str
    song_count: Optional[int] = None
    release_date: Optional[str] = None

class AlbumsResponse(BaseModel):
    albums: List[AlbumResponse]

class DatabaseSummaryResponse(BaseModel):
    total_songs: int
    total_artists: int
    total_albums: int
    songs_with_features: int
    average_songs_per_artist: float
    average_songs_per_album: float

class AllDataResponse(BaseModel):
    summary: DatabaseSummaryResponse
    artists: List[ArtistResponse]
    albums: List[AlbumResponse]
    songs: List[SongResponse]

# Routes
@router.post("/display_database")
async def display_database():
    try:
        await fetch_and_store_songs()
        return {"message": "Database updated and displayed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary", response_model=DatabaseSummaryResponse)
async def get_database_summary():
    """Get a summary of the database contents"""
    try:
        summary = display_database_summary()
        return DatabaseSummaryResponse(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/artists", response_model=ArtistsResponse)
async def get_all_artists() -> ArtistsResponse:
    """Get all artists in the database"""
    try:
        artists_data = display_all_artists()
        # Map the database fields to our model fields
        artists = [
            ArtistResponse(
                id=str(artist['ID']),
                name=artist['Name'],
                album_count=artist.get('AlbumCount'),
                song_count=artist.get('SongCount')
            ) for artist in artists_data
        ]
        return ArtistsResponse(artists=artists)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/albums", response_model=AlbumsResponse)
async def get_all_albums() -> AlbumsResponse:
    """Get all albums in the database"""
    try:
        albums_data = display_all_albums()
        # Map the database fields to our model fields
        albums = []
        for album in albums_data:
            try:
                album_response = AlbumResponse(
                    id=str(album.get('ID', '')),
                    name=album.get('Album Name', 'Unknown Album'),
                    artist=album.get('Artist Name', 'Unknown Artist'),
                    song_count=album.get('SongCount'),
                    release_date=album.get('Release Date')
                )
                albums.append(album_response)
            except Exception as e:
                print(f"Error processing album: {album}, Error: {str(e)}")
                continue
        
        return AlbumsResponse(albums=albums)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/songs", response_model=SongsResponse)
async def get_songs():
    """Get all songs from the database"""
    try:
        # Get the database path
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(root_dir, "../Database/music_app.db")
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all songs with their artist and album names
        cursor.execute("""
            SELECT s.song_id, s.name as song_name, 
                   ar.name as artist_name, 
                   al.name as album_name,
                   s.duration, s.tempo,
                   s.spectral_centroid, s.spectral_rolloff,
                   s.spectral_contrast, s.chroma_mean,
                   s.chroma_std, s.onset_strength,
                   s.zero_crossing_rate, s.rms_energy
            FROM Song s
            JOIN Album al ON s.album_id = al.album_id
            JOIN Artist ar ON al.artist_id = ar.artist_id
        """)
        
        # Fetch all results
        songs = cursor.fetchall()
        
        def convert_to_float(value):
            if value is None:
                return None
            if isinstance(value, bytes):
                try:
                    # Try to convert binary data to float
                    return float.fromhex(value.hex())
                except (ValueError, AttributeError):
                    return None
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        
        # Convert to list of dictionaries, handling binary data
        result = []
        for song in songs:
            song_dict = {
                "id": str(song['song_id']),
                "name": song['song_name'].decode('utf-8', errors='replace') if isinstance(song['song_name'], bytes) else song['song_name'],
                "artist": song['artist_name'].decode('utf-8', errors='replace') if isinstance(song['artist_name'], bytes) else song['artist_name'],
                "album": song['album_name'].decode('utf-8', errors='replace') if isinstance(song['album_name'], bytes) else song['album_name'],
                "duration": convert_to_float(song['duration']),
                "tempo": convert_to_float(song['tempo']),
                "spectral_centroid": convert_to_float(song['spectral_centroid']),
                "spectral_rolloff": convert_to_float(song['spectral_rolloff']),
                "spectral_contrast": convert_to_float(song['spectral_contrast']),
                "chroma_mean": convert_to_float(song['chroma_mean']),
                "chroma_std": convert_to_float(song['chroma_std']),
                "onset_strength": convert_to_float(song['onset_strength']),
                "zero_crossing_rate": convert_to_float(song['zero_crossing_rate']),
                "rms_energy": convert_to_float(song['rms_energy'])
            }
            result.append(SongResponse(**song_dict))
        
        return SongsResponse(songs=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()

@router.post("/populate")
async def populate_database():
    """Populate the database with initial data"""
    try:
        await fetch_and_store_songs()
        return {"message": "Database populated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all", response_model=AllDataResponse)
async def get_all_data():
    """Get all database contents"""
    try:
        summary = display_database_summary()
        artists_data = display_all_artists()
        albums_data = display_all_albums()
        songs_data = display_all_songs()
        
        return AllDataResponse(
            summary=DatabaseSummaryResponse(**summary),
            artists=[ArtistResponse(**artist) for artist in artists_data],
            albums=[AlbumResponse(**album) for album in albums_data],
            songs=[SongResponse(**song) for song in songs_data]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
