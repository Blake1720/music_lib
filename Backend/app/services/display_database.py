import sqlite3
import os
from typing import List, Dict, Any
from tabulate import tabulate

def get_db_connection():
    """Get a connection to the SQLite database"""
    # Get the root directory (two levels up from this file)
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    db_path = os.path.join(root_dir, "Database/music_app.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

def check_database_tables():
    """Check if tables exist and have data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all tables
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
    """
    Display all artists in the database.
    Returns a list of dictionaries containing artist information.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT artist_id, name 
            FROM Artist 
            ORDER BY name
        """)
        artists = cursor.fetchall()
        
        print("\n=== All Artists ===\n")
        if not artists:
            print("No artists found in the database")
            return []
        
        # Convert to list of dictionaries for better formatting
        artist_list = [{"ID": row["artist_id"], "Name": row["name"]} for row in artists]
        print(tabulate(artist_list, headers="keys", tablefmt="grid"))
        return artist_list
    except sqlite3.OperationalError as e:
        print(f"Error accessing artists table: {e}")
        return []
    finally:
        conn.close()

def display_all_albums() -> List[Dict[str, Any]]:
    """
    Display all albums in the database with their artists.
    Returns a list of dictionaries containing album information.
    """
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
        
        # Convert to list of dictionaries for better formatting
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
    """
    Display all songs in the database with their albums and artists.
    Returns a list of dictionaries containing song information.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT s.song_id, s.name as song_name, al.name as album_name, 
                   ar.name as artist_name, s.genre, s.duration
            FROM Song s
            JOIN Album al ON s.album_id = al.album_id
            JOIN Artist ar ON al.artist_id = ar.artist_id
            ORDER BY ar.name, al.name, s.name
        """)
        songs = cursor.fetchall()
        
        print("\n=== All Songs ===\n")
        if not songs:
            print("No songs found in the database")
            return []
        
        # Convert to list of dictionaries for better formatting
        song_list = [
            {
                "ID": row["song_id"],
                "Song Name": row["song_name"],
                "Album": row["album_name"],
                "Artist": row["artist_name"],
                "Genre": row["genre"],
                "Duration (s)": row["duration"]
            } for row in songs
        ]
        print(tabulate(song_list, headers="keys", tablefmt="grid"))
        return song_list
    except sqlite3.OperationalError as e:
        print(f"Error accessing songs table: {e}")
        return []
    finally:
        conn.close()

def display_database_summary():
    """
    Display a summary of the database contents including counts of artists, albums, and songs.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get counts
        cursor.execute("SELECT COUNT(*) FROM Artist")
        artist_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Album")
        album_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Song")
        song_count = cursor.fetchone()[0]
        
        print("\n=== Database Summary ===\n")
        summary = [
            {"Category": "Artists", "Count": artist_count},
            {"Category": "Albums", "Count": album_count},
            {"Category": "Songs", "Count": song_count}
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
