'''
This file is used to create the database.
'''
import sqlite3
import os

def create_music_app_db():
    # Target the database in the Database directory
    db_path = os.path.join(os.path.dirname(__file__), "music_app.db")
    print(f"Creating database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop existing tables if they exist
    tables = [
        "User", "Artist", "Album", "Song", 
        "Playlist", "Playlist_Song", "History"
    ]
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()

    cursor.execute("""
    CREATE TABLE User (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER
    );
    """)

    cursor.execute("""
    CREATE TABLE Artist (
        artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    );
    """)

    cursor.execute("""
    CREATE TABLE Album (
        album_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        artist_id INTEGER,
        date_created DATETIME,
        album_url TEXT UNIQUE,
        FOREIGN KEY (artist_id) REFERENCES Artist(artist_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE Song (
        song_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        album_id INTEGER NOT NULL,
        genre TEXT,
        duration REAL,
        tempo REAL,
        spectral_centroid REAL,
        spectral_rolloff REAL,
        spectral_contrast REAL,
        chroma_mean REAL,
        chroma_std REAL,
        onset_strength REAL,
        zero_crossing_rate REAL,
        rms_energy REAL,
        FOREIGN KEY (album_id) REFERENCES Album(album_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE Playlist (
        user_id INTEGER,
        name TEXT,
        date_created DATETIME,
        PRIMARY KEY (user_id, name),
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE Playlist_Song (
        user_id INTEGER,
        playlist_name TEXT,
        song_id INTEGER,
        PRIMARY KEY (user_id, playlist_name, song_id),
        FOREIGN KEY (user_id, playlist_name) REFERENCES Playlist(user_id, name),
        FOREIGN KEY (song_id) REFERENCES Song(song_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE History (
        user_id INTEGER,
        song_id INTEGER,
        played_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, played_at),
        FOREIGN KEY (user_id) REFERENCES User(user_id),
        FOREIGN KEY (song_id) REFERENCES Song(song_id)
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_music_app_db()