from fastapi import APIRouter, HTTPException, Query
from typing import List, Any, Optional
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
class UserCreateRequest(BaseModel):
    name: str
    age: Optional[int] = None

class UserResponse(BaseModel):
    user_id: int
    name: str
    age: Optional[int]


# Routes
from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
import sqlite3
import os

router = APIRouter()

class UserCreateRequest(BaseModel):
    name: str
    age: Optional[int] = None

class UserResponse(BaseModel):
    user_id: int
    name: str
    age: Optional[int]

@router.post("/create", response_model=UserResponse)
async def create_user(request: UserCreateRequest):
    conn = None
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(root_dir, "../Database/music_app.db")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT user_id FROM User WHERE name = ?", (request.name,))
        existing_user = cursor.fetchone()
        if existing_user:
            raise HTTPException(status_code=409, detail="Username already exists")

        cursor.execute(
            "INSERT INTO User (name, age) VALUES (?, ?)",
            (request.name, request.age)
        )
        conn.commit()

        user_id = cursor.lastrowid
        return UserResponse(user_id=user_id, name=request.name, age=request.age)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()

