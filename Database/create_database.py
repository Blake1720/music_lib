
import sqlite3

def create_music_app_db(db_path="music_app.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

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
        name TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE Album (
        album_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        artist_id INTEGER,
        date_created DATETIME,
        FOREIGN KEY (artist_id) REFERENCES Artist(artist_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE Song (
        song_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        album_id INTEGER,
        genre TEXT,
        duration INTEGER,
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
