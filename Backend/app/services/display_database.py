'''
This file is used to display the contents of the database.
'''
import sqlite3
import os
from typing import List, Dict, Any
from tabulate import tabulate

def get_db_connection():
    """Get a connection to the SQLite database"""
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    db_path = os.path.join(root_dir, "Database/music_app.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def check_database_tables():
    """Check if tables exist and have data"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print("\n=== Database Tables ===\n")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Table: {table_name}, Row count: {count}")
    
    conn.close()

def display_all_artists() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT artist_id, name FROM Artist ORDER BY name")
        artists = cursor.fetchall()

        print("\n=== All Artists ===\n")
        if not artists:
            print("No artists found in the database")
            return []

        artist_list = [{"ID": row["artist_id"], "Name": row["name"]} for row in artists]
        print(tabulate(artist_list, headers="keys", tablefmt="grid"))
        return artist_list
    except sqlite3.OperationalError as e:
        print(f"Error accessing artists table: {e}")
        return []
    finally:
        conn.close()

def display_all_albums() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT a.album_id, a.name as album_name, ar.name as artist_name, a.date_created
            FROM Album a
            JOIN Artist ar ON a.artist_id = ar.artist_id
            ORDER BY ar.name, a.name
        """)
        albums = cursor.fetchall()

        print("\n=== All Albums ===\n")
        if not albums:
            print("No albums found in the database")
            return []

        album_list = [
            {
                "ID": row["album_id"],
                "Album Name": row["album_name"],
                "Artist": row["artist_name"],
                "Date Created": row["date_created"]
            } for row in albums
        ]
        print(tabulate(album_list, headers="keys", tablefmt="grid"))
        return album_list
    except sqlite3.OperationalError as e:
        print(f"Error accessing albums table: {e}")
        return []
    finally:
        conn.close()

def display_all_songs() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()

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

    try:
        cursor.execute("""
            SELECT s.song_id, s.name as song_name, al.name as album_name, 
                   ar.name as artist_name, s.genre,
                   s.duration, s.tempo, s.spectral_centroid, s.spectral_rolloff,
                   s.spectral_contrast, s.chroma_mean, s.chroma_std,
                   s.onset_strength, s.zero_crossing_rate, s.rms_energy
            FROM Song s
            JOIN Album al ON s.album_id = al.album_id
            JOIN Artist ar ON al.artist_id = ar.artist_id
            ORDER BY ar.name, al.name, s.name
        """)
        songs = cursor.fetchall()

        song_list = []
        for row in songs:
            song = {
                "id": str(row["song_id"]),
                "name": row["song_name"].decode("utf-8", errors="replace") if isinstance(row["song_name"], bytes) else row["song_name"],
                "album": row["album_name"].decode("utf-8", errors="replace") if isinstance(row["album_name"], bytes) else row["album_name"],
                "artist": row["artist_name"].decode("utf-8", errors="replace") if isinstance(row["artist_name"], bytes) else row["artist_name"],
                "genre": row["genre"],
                "duration": convert_to_float(row["duration"]),
                "tempo": convert_to_float(row["tempo"]),
                "spectral_centroid": convert_to_float(row["spectral_centroid"]),
                "spectral_rolloff": convert_to_float(row["spectral_rolloff"]),
                "spectral_contrast": convert_to_float(row["spectral_contrast"]),
                "chroma_mean": convert_to_float(row["chroma_mean"]),
                "chroma_std": convert_to_float(row["chroma_std"]),
                "onset_strength": convert_to_float(row["onset_strength"]),
                "zero_crossing_rate": convert_to_float(row["zero_crossing_rate"]),
                "rms_energy": convert_to_float(row["rms_energy"]),
            }
            song_list.append(song)

        return song_list

    except Exception as e:
        print("🔥 Error in display_all_songs:", e)
        return []
    finally:
        conn.close()


def display_database_summary():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM Artist")
        artist_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Album")
        album_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Song")
        song_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT 
                COUNT(*) as total_songs,
                COUNT(CASE WHEN duration IS NOT NULL THEN 1 END) as songs_with_duration,
                COUNT(CASE WHEN tempo IS NOT NULL THEN 1 END) as songs_with_tempo
            FROM Song
        """)
        stats = cursor.fetchone()

        print("\n=== Database Summary ===\n")
        summary = [
            {"Category": "Artists", "Count": artist_count},
            {"Category": "Albums", "Count": album_count},
            {"Category": "Songs", "Count": song_count},
            {"Category": "Songs with Duration", "Count": stats["songs_with_duration"]},
            {"Category": "Songs with Tempo", "Count": stats["songs_with_tempo"]}
        ]
        print(tabulate(summary, headers="keys", tablefmt="grid"))
    except sqlite3.OperationalError as e:
        print(f"Error accessing database tables: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_database_tables()
    display_database_summary()
    display_all_artists()
    display_all_albums()
    display_all_songs()