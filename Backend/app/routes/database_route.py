#routes for the database

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from services.propagateDB import fetch_and_store_songs
from services.display_database import (
    display_all_artists,
    display_all_albums,
    display_all_songs,
    display_database_summary
)

router = APIRouter()

@router.post("/display_database")
async def display_database():
    try:
        await fetch_and_store_songs()
        return {"message": "Database updated and displayed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_database_summary():
    """Get a summary of the database contents"""
    try:
        display_database_summary()
        return {"message": "Database summary displayed in console"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/artists")
async def get_all_artists() -> List[Dict[str, Any]]:
    """Get all artists in the database"""
    try:
        artists = display_all_artists()
        return {"artists": artists}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/albums")
async def get_all_albums() -> List[Dict[str, Any]]:
    """Get all albums in the database"""
    try:
        albums = display_all_albums()
        return {"albums": albums}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/songs")
async def get_all_songs() -> List[Dict[str, Any]]:
    """Get all songs in the database"""
    try:
        songs = display_all_songs()
        return {"songs": songs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all")
async def get_all_data():
    """Get all database contents"""
    try:
        summary = display_database_summary()
        artists = display_all_artists()
        albums = display_all_albums()
        songs = display_all_songs()
        return {
            "summary": summary,
            "artists": artists,
            "albums": albums,
            "songs": songs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
