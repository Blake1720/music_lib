import sqlite3

def get_connection():
    conn = sqlite3.connect("music_library.db")
    with conn:  # Ensure the PRAGMA setting applies
        conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def setup():
	# Connect to SQLite database (or create if it doesn't exist)
	conn = get_connection()
	cursor = conn.cursor()

	# Enable foreign key constraints
	cursor.execute("PRAGMA foreign_keys = ON;")

	# Create User table
	cursor.execute("""
	    CREATE TABLE IF NOT EXISTS user (
	        id INTEGER PRIMARY KEY AUTOINCREMENT,
	        name TEXT NOT NULL UNIQUE
	    )
	""")

	# Create Artist table
	cursor.execute("""
	    CREATE TABLE IF NOT EXISTS artist (
	        id INTEGER PRIMARY KEY AUTOINCREMENT,
	        name TEXT NOT NULL UNIQUE
	    )
	""")

	# Create Album table
	cursor.execute("""
	    CREATE TABLE IF NOT EXISTS album (
	        id INTEGER PRIMARY KEY AUTOINCREMENT,
	        name TEXT NOT NULL,
	        artist_id INTEGER NOT NULL,
	        FOREIGN KEY (artist_id) REFERENCES artist(id) ON DELETE CASCADE
	    )
	""")

	# Create Song table
	cursor.execute("""
	    CREATE TABLE IF NOT EXISTS song (
	        id INTEGER PRIMARY KEY AUTOINCREMENT,
	        name TEXT NOT NULL,
	        album_id INTEGER NOT NULL,
	        FOREIGN KEY (album_id) REFERENCES album(id) ON DELETE CASCADE
	    )
	""")

	# Create Playlist table
	cursor.execute("""
	    CREATE TABLE IF NOT EXISTS playlist (
	        id INTEGER PRIMARY KEY AUTOINCREMENT,
	        name TEXT NOT NULL,
	        user_id INTEGER NOT NULL,
	        FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
	    )
	""")

	# Create Playlist-Song many-to-many relationship table
	cursor.execute("""
	    CREATE TABLE IF NOT EXISTS playlist_song (
	        playlist_id INTEGER NOT NULL,
	        song_id INTEGER NOT NULL,
	        PRIMARY KEY (playlist_id, song_id),
	        FOREIGN KEY (playlist_id) REFERENCES playlist(id) ON DELETE CASCADE,
	        FOREIGN KEY (song_id) REFERENCES song(id) ON DELETE CASCADE
	    )
	""")

	# Create History table to track song plays
	cursor.execute("""
	    CREATE TABLE IF NOT EXISTS history (
	        id INTEGER PRIMARY KEY AUTOINCREMENT,
	        user_id INTEGER NOT NULL,
	        song_id INTEGER NOT NULL,
	        played_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	        FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
	        FOREIGN KEY (song_id) REFERENCES song(id) ON DELETE CASCADE
	    )
	""")

	# Commit and close
	conn.commit()
	conn.close()
