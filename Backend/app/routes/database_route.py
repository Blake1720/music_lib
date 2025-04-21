'''
This file creates the routes for the database.
'''
from fastapi import APIRouter, HTTPException, Query, Body, Form, UploadFile, File
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
    album_url: Optional[str] = None
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
    url: Optional[str] = None
    songs: List[SongResponse] = []
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


class SearchResults(BaseModel):
    artists: List[ArtistResponse] = []
    albums: List[AlbumResponse] = []
    songs: List[SongResponse] = []

class PlaylistInfo(BaseModel):
    name: str
    date_created: str
    song_count: int
    image_url: Optional[str] = None

class UserPlaylistsResponse(BaseModel):
    username: str
    playlists: List[PlaylistInfo]

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
                    artist=album.get('Artist', 'Unknown Artist'),
                    url=album.get('url'),
                    song_count=album.get('SongCount'),
                    release_date=album.get('Release Date')
                )
                albums.append(album_response)
            except Exception as e:
                print(f"Error processing album: {album}, Error: {str(e)}")
                continue
        print("Album keys:", album)

        return AlbumsResponse(albums=albums)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/songs", response_model=SongsResponse)
async def get_songs(sort_by: Optional[str] = Query(None, description="Sort by: 'name_asc', 'name_desc'")):
    """Get all songs from the database"""
    try:
        # Get the database path
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(root_dir, "../Database/music_app.db")
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Base query
        query = """
            SELECT s.song_id, s.name as song_name, 
                   ar.name as artist_name, 
                   al.name as album_name,
                   al.album_url as album_url,
                   s.duration, s.tempo,
                   s.spectral_centroid, s.spectral_rolloff,
                   s.spectral_contrast, s.chroma_mean,
                   s.chroma_std, s.onset_strength,
                   s.zero_crossing_rate, s.rms_energy
            FROM Song s
            JOIN Album al ON s.album_id = al.album_id
            JOIN Artist ar ON al.artist_id = ar.artist_id
        """

        # Add ORDER BY clause based on sort_by parameter
        if sort_by == "name_desc":
            query += " ORDER BY s.name DESC"
        elif sort_by == "name_asc":
            query += " ORDER BY s.name ASC"
        else:
            query += " ORDER BY s.song_id ASC"  # Default sorting by ID

        cursor.execute(query)
        
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
                "album_url": song['album_url'],
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


@router.get("/search", response_model=SearchResults)
async def search_database(
    q: str = Query(..., description="Search query"),
    min_songs: Optional[int] = Query(None, description="Minimum number of songs for artists"),
    sort_by: Optional[str] = Query(None, description="Sort by: 'song_count_asc', 'song_count_desc', 'name_asc', 'name_desc'"),
    album_sort: Optional[str] = Query(None, description="Sort albums by: 'song_count_asc', 'song_count_desc', 'name_asc', 'name_desc'"),
    song_sort: Optional[str] = Query(None, description="Sort songs by: 'name_asc', 'name_desc'")
):
    """Search for matching artists, albums, and songs by name."""
    try:
        query = q.lower()

        # Get the database path
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(root_dir, "../Database/music_app.db")
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get matching artists with song counts
        artist_query = """
            SELECT ar.artist_id, ar.name,
                   COUNT(DISTINCT s.song_id) as song_count
            FROM Artist ar
            LEFT JOIN Album al ON ar.artist_id = al.artist_id
            LEFT JOIN Song s ON al.album_id = s.album_id
            WHERE LOWER(ar.name) LIKE ?
            GROUP BY ar.artist_id, ar.name
        """
        
        # Add HAVING clause if min_songs is specified
        if min_songs is not None:
            artist_query += f" HAVING song_count >= {min_songs}"
        
        # Add ORDER BY clause based on sort_by parameter
        if sort_by == "song_count_desc":
            artist_query += " ORDER BY song_count DESC, ar.artist_id ASC"
        elif sort_by == "song_count_asc":
            artist_query += " ORDER BY song_count ASC, ar.artist_id ASC"
        elif sort_by == "name_desc":
            artist_query += " ORDER BY ar.name DESC, ar.artist_id ASC"
        elif sort_by == "name_asc":
            artist_query += " ORDER BY ar.name ASC, ar.artist_id ASC"
        else:
            artist_query += " ORDER BY ar.artist_id ASC"  # Default sorting by ID
        
        cursor.execute(artist_query, (f"%{query}%",))
        artists_rows = cursor.fetchall()
        matching_artists = [
            ArtistResponse(
                id=str(row["artist_id"]),
                name=row["name"],
                song_count=row["song_count"]
            )
            for row in artists_rows
        ]

        # Get matching albums with URLs
        album_query = """
            SELECT a.album_id, a.name, ar.name as artist_name, a.album_url,
                   COUNT(s.song_id) as song_count
            FROM Album a
            JOIN Artist ar ON a.artist_id = ar.artist_id
            LEFT JOIN Song s ON a.album_id = s.album_id
            WHERE LOWER(a.name) LIKE ?
            GROUP BY a.album_id, a.name, ar.name, a.album_url
        """

        # Add ORDER BY clause based on album_sort parameter
        if album_sort == "song_count_desc":
            album_query += " ORDER BY song_count DESC, a.album_id ASC"
        elif album_sort == "song_count_asc":
            album_query += " ORDER BY song_count ASC, a.album_id ASC"
        elif album_sort == "name_desc":
            album_query += " ORDER BY a.name DESC, a.album_id ASC"
        elif album_sort == "name_asc":
            album_query += " ORDER BY a.name ASC, a.album_id ASC"
        else:
            album_query += " ORDER BY a.album_id ASC"  # Default sorting by ID

        cursor.execute(album_query, (f"%{query}%",))
        albums_rows = cursor.fetchall()
        matching_albums = [
            AlbumResponse(
                id=str(row["album_id"]),
                name=row["name"],
                artist=row["artist_name"],
                url=row["album_url"],
                song_count=row["song_count"]
            )
            for row in albums_rows
        ]

        # Get matching songs with album URLs
        song_query = """
            SELECT s.song_id, s.name as song_name, 
                   ar.name as artist_name, 
                   al.name as album_name,
                   al.album_url as album_url,
                   s.duration
            FROM Song s
            JOIN Album al ON s.album_id = al.album_id
            JOIN Artist ar ON al.artist_id = ar.artist_id
            WHERE LOWER(s.name) LIKE ?
        """

        # Add ORDER BY clause based on song_sort parameter
        if song_sort == "name_desc":
            song_query += " ORDER BY s.name DESC, s.song_id ASC"
        elif song_sort == "name_asc":
            song_query += " ORDER BY s.name ASC, s.song_id ASC"
        else:
            song_query += " ORDER BY s.song_id ASC"  # Default sorting by ID

        cursor.execute(song_query, (f"%{query}%",))
        songs_rows = cursor.fetchall()
        matching_songs = [
            SongResponse(
                id=str(row["song_id"]),
                name=row["song_name"],
                artist=row["artist_name"],
                album=row["album_name"],
                album_url=row["album_url"],
                duration=row["duration"]
            )
            for row in songs_rows
        ]

        return SearchResults(
            artists=matching_artists,
            albums=matching_albums,
            songs=matching_songs
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()
    
@router.get("/albums/{album_id}/songs", response_model=AlbumResponse)
async def get_songs_by_album(album_id: int):
    """Get all songs that belong to a specific album by album ID"""
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(root_dir, "../Database/music_app.db")

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT s.song_id, s.name as song_name, 
                   ar.name as artist_name, 
                   al.name as album_name,
                   al.album_url as album_url,
                   s.duration, s.tempo,
                   s.spectral_centroid, s.spectral_rolloff,
                   s.spectral_contrast, s.chroma_mean,
                   s.chroma_std, s.onset_strength,
                   s.zero_crossing_rate, s.rms_energy
            FROM Song s
            JOIN Album al ON s.album_id = al.album_id
            JOIN Artist ar ON al.artist_id = ar.artist_id
            WHERE s.album_id = ?
        """, (album_id,))

        songs = cursor.fetchall()

        def convert_to_float(value):
            if value is None:
                return None
            if isinstance(value, bytes):
                try:
                    return float.fromhex(value.hex())
                except Exception:
                    return None
            try:
                return float(value)
            except Exception:
                return None

        result = []
        for row in songs:
            song_dict = {
                "id": str(row["song_id"]),
                "name": row["song_name"],
                "album": row["album_name"],
                "artist": row["artist_name"],
                "album_url": row["album_url"],
                "duration": convert_to_float(row["duration"]),
                "tempo": convert_to_float(row["tempo"]),
                "spectral_centroid": convert_to_float(row["spectral_centroid"]),
                "spectral_rolloff": convert_to_float(row["spectral_rolloff"]),
                "spectral_contrast": convert_to_float(row["spectral_contrast"]),
                "chroma_mean": convert_to_float(row["chroma_mean"]),
                "chroma_std": convert_to_float(row["chroma_std"]),
                "onset_strength": convert_to_float(row["onset_strength"]),
                "zero_crossing_rate": convert_to_float(row["zero_crossing_rate"]),
                "rms_energy": convert_to_float(row["rms_energy"])
            }
            result.append(SongResponse(**song_dict))

        return AlbumResponse(
            id=str(album_id),
            name=row["album_name"],
            artist=row["artist_name"],
            url=row["album_url"],
            songs=result
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.get("/playlists", response_model=UserPlaylistsResponse)
async def get_user_playlists(username: str = Query(..., description="Username to look up playlists")):
    conn = None
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(root_dir, "../Database/music_app.db")

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # First check if user exists
        cursor.execute("SELECT user_id FROM User WHERE name = ?", (username,))
        user_row = cursor.fetchone()
        if not user_row:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")

        user_id = user_row["user_id"]

        # Get all playlists for the user
        cursor.execute("""
            SELECT p.name, p.date_created, p.image_url, COUNT(ps.song_id) as song_count
            FROM Playlist p
            LEFT JOIN Playlist_Song ps ON p.user_id = ps.user_id AND p.name = ps.playlist_name
            WHERE p.user_id = ?
            GROUP BY p.name, p.date_created, p.image_url
            ORDER BY p.date_created DESC
        """, (user_id,))

        playlists = []
        for row in cursor.fetchall():
            try:
                playlist = PlaylistInfo(
                    name=row["name"],
                    date_created=row["date_created"],
                    song_count=row["song_count"],
                    image_url=row["image_url"]
                )
                playlists.append(playlist)
            except Exception as e:
                print(f"Error processing playlist row: {e}")
                continue

        return UserPlaylistsResponse(username=username, playlists=playlists)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching playlists: {str(e)}")
    finally:
        if conn:
            conn.close()

@router.get("/playlists/songs", response_model=List[SongResponse])
async def get_songs_from_playlist(
    username: str = Query(...),
    playlist_name: str = Query(...)
):
    """Fetch all songs from a given playlist for a user"""
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(root_dir, "../Database/music_app.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT user_id FROM User WHERE name = ?", (username,))
        user_row = cursor.fetchone()
        if not user_row:
            raise HTTPException(status_code=404, detail="User not found")
        user_id = user_row["user_id"]

        cursor.execute("""
            SELECT s.song_id, s.name AS song_name, ar.name AS artist_name, 
                   al.name AS album_name, al.album_url AS album_url, s.duration
            FROM Playlist_Song ps
            JOIN Song s ON ps.song_id = s.song_id
            JOIN Album al ON s.album_id = al.album_id
            JOIN Artist ar ON al.artist_id = ar.artist_id
            WHERE ps.user_id = ? AND ps.playlist_name = ?
        """, (user_id, playlist_name))

        rows = cursor.fetchall()
        songs = [
            SongResponse(
                id=str(row["song_id"]),
                name=row["song_name"],
                artist=row["artist_name"],
                album=row["album_name"],
                album_url=row["album_url"],
                duration=row["duration"]
            )
            for row in rows
        ]

        return songs

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@router.delete("/playlists")
async def delete_playlist(
    username: str = Query(..., description="Username of the playlist owner"),
    playlist_name: str = Query(..., description="Name of the playlist to delete")
):
    """Delete a playlist and all its songs"""
    conn = None
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(root_dir, "../Database/music_app.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get user_id
        cursor.execute("SELECT user_id FROM User WHERE name = ?", (username,))
        user_row = cursor.fetchone()
        if not user_row:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")
        user_id = user_row[0]

        # Delete playlist songs first (due to foreign key constraint)
        cursor.execute("""
            DELETE FROM Playlist_Song 
            WHERE user_id = ? AND playlist_name = ?
        """, (user_id, playlist_name))

        # Delete playlist
        cursor.execute("""
            DELETE FROM Playlist 
            WHERE user_id = ? AND name = ?
        """, (user_id, playlist_name))

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Playlist not found")

        conn.commit()
        return {"message": "Playlist deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting playlist: {str(e)}")
    finally:
        if conn:
            conn.close()

@router.post("/playlists/songs")
async def add_songs_to_playlist(
    username: str = Query(..., description="Username of the playlist owner"),
    playlist_name: str = Query(..., description="Name of the playlist"),
    song_ids: List[str] = Body(..., description="List of song IDs to add")
):
    """Add songs to an existing playlist"""
    conn = None
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(root_dir, "../Database/music_app.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get user_id
        cursor.execute("SELECT user_id FROM User WHERE name = ?", (username,))
        user_row = cursor.fetchone()
        if not user_row:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")
        user_id = user_row[0]

        # Verify playlist exists
        cursor.execute("""
            SELECT 1 FROM Playlist 
            WHERE user_id = ? AND name = ?
        """, (user_id, playlist_name))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Playlist not found")

        # Add each song to the playlist
        for song_id in song_ids:
            cursor.execute("""
                INSERT OR IGNORE INTO Playlist_Song (user_id, playlist_name, song_id)
                VALUES (?, ?, ?)
            """, (user_id, playlist_name, song_id))

        conn.commit()
        return {"message": f"Added {len(song_ids)} songs to playlist successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding songs to playlist: {str(e)}")
    finally:
        if conn:
            conn.close()

@router.put("/playlists/rename")
async def rename_playlist(
    username: str = Query(..., description="Username of the playlist owner"),
    old_name: str = Query(..., description="Current playlist name"),
    new_name: str = Query(..., description="New playlist name")
):
    """Rename an existing playlist"""
    conn = None
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(root_dir, "../Database/music_app.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get user_id
        cursor.execute("SELECT user_id FROM User WHERE name = ?", (username,))
        user_row = cursor.fetchone()
        if not user_row:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")
        user_id = user_row[0]

        # Check if new name already exists
        cursor.execute("""
            SELECT 1 FROM Playlist 
            WHERE user_id = ? AND name = ?
        """, (user_id, new_name))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail=f"Playlist name '{new_name}' already exists")

        # Update playlist name
        cursor.execute("""
            UPDATE Playlist 
            SET name = ?
            WHERE user_id = ? AND name = ?
        """, (new_name, user_id, old_name))

        # Also update the name in Playlist_Song table
        cursor.execute("""
            UPDATE Playlist_Song 
            SET playlist_name = ?
            WHERE user_id = ? AND playlist_name = ?
        """, (new_name, user_id, old_name))

        conn.commit()
        return {"message": f"Playlist renamed from '{old_name}' to '{new_name}'"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error renaming playlist: {str(e)}")
    finally:
        if conn:
            conn.close()

@router.post("/playlists/image")
async def upload_playlist_image(
    username: str = Form(...),
    playlist_name: str = Form(...),
    image: UploadFile = File(...)
):
    """Upload an image for a playlist"""
    conn = None
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(root_dir, "../Database/music_app.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get user_id
        cursor.execute("SELECT user_id FROM User WHERE name = ?", (username,))
        user_row = cursor.fetchone()
        if not user_row:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")
        user_id = user_row[0]

        # Verify playlist exists
        cursor.execute("""
            SELECT 1 FROM Playlist 
            WHERE user_id = ? AND name = ?
        """, (user_id, playlist_name))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Playlist not found")

        # Save the image file
        image_dir = os.path.join(root_dir, "../Frontend/public/playlist_images")
        os.makedirs(image_dir, exist_ok=True)
        
        # Generate a unique filename
        file_extension = os.path.splitext(image.filename)[1]
        unique_filename = f"{user_id}_{playlist_name}{file_extension}"
        file_path = os.path.join(image_dir, unique_filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        
        # Update the playlist with the image URL
        image_url = f"/playlist_images/{unique_filename}"
        cursor.execute("""
            UPDATE Playlist 
            SET image_url = ?
            WHERE user_id = ? AND name = ?
        """, (image_url, user_id, playlist_name))
        
        conn.commit()
        return {"image_url": image_url}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading playlist image: {str(e)}")
    finally:
        if conn:
            conn.close()