import os
import sqlite3
import random
import string
import time
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Debug prints
print(f"Current file path: {__file__}")
print(f"Current working directory: {os.getcwd()}")

# Load environment variables from project root
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env')
print(f"Looking for .env at: {env_path}")
print(f".env exists: {os.path.exists(env_path)}")

load_dotenv(env_path)

# Spotify authentication
auth_manager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Verify authentication by making a test call
try:
    test_features = sp.audio_features(['4xdBrk0nFZaP54vvZj0yx7'])
    print("Authentication successful!")
except Exception as e:
    print(f"Authentication failed: {e}")
    print("Please check your Spotify API credentials and ensure they have the correct permissions.")

# SQLite connection
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                      "Database", "music_app.db")
print(f"Database path: {DB_PATH}")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

def get_random_query():
    return random.choice(string.ascii_lowercase)

def insert_artist(name):
    cur.execute("INSERT OR IGNORE INTO Artist (name) VALUES (?)", (name,))
    cur.execute("SELECT artist_id FROM Artist WHERE name = ?", (name,))
    return cur.fetchone()[0]

def insert_album(name, artist_id):
    cur.execute("INSERT OR IGNORE INTO Album (name, artist_id, date_created) VALUES (?, ?, datetime('now'))",
                (name, artist_id))
    cur.execute("SELECT album_id FROM Album WHERE name = ? AND artist_id = ?", (name, artist_id))
    return cur.fetchone()[0]

def insert_song(data, album_id, genre, popularity, features=None):
    try:
        if features:
            # If we have audio features, use them
            cur.execute("""
            INSERT OR IGNORE INTO Song (
                name, album_id, genre, duration, 
                instrumentalness, acousticness, danceability, 
                liveness, tempo, popularity
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                data['name'], 
                album_id, 
                genre, 
                data['duration_ms'] // 1000,
                features['instrumentalness'],
                features['acousticness'],
                features['danceability'],
                features['liveness'],
                features['tempo'],
                popularity
            ))
        else:
            # If no audio features, insert with NULL values
            cur.execute("""
            INSERT OR IGNORE INTO Song (
                name, album_id, genre, duration, 
                instrumentalness, acousticness, danceability, 
                liveness, tempo, popularity
            ) VALUES (?, ?, ?, ?, NULL, NULL, NULL, NULL, NULL, ?)""", (
                data['name'], 
                album_id, 
                genre, 
                data['duration_ms'] // 1000,
                popularity
            ))
    except Exception as e:
        print(f"Error inserting song {data['name']}: {e}")

def fetch_and_store_songs(limit=100):
    seen_ids = set()
    total_added = 0
    batch_size = 50  # Number of tracks to process in each batch
    tracks_to_process = []  # Store tracks for batch processing

    while total_added < limit:
        try:
            query = get_random_query()
            results = sp.search(q=query, type='track', limit=batch_size)
            
            # Collect tracks for batch processing
            for item in results['tracks']['items']:
                if total_added >= limit:
                    break
                if item['id'] in seen_ids:
                    continue
                seen_ids.add(item['id'])
                tracks_to_process.append(item)

            # Process tracks in batches of 100 (max allowed by audio_features endpoint)
            while tracks_to_process:
                batch = tracks_to_process[:100]
                tracks_to_process = tracks_to_process[100:]
                
                # Get audio features for the batch
                track_ids = [track['id'] for track in batch]
                try:
                    audio_features_batch = sp.audio_features(track_ids)
                    print(f"Successfully fetched audio features for {len(audio_features_batch)} tracks")
                except Exception as e:
                    print(f"Error fetching audio features: {e}")
                    audio_features_batch = [None] * len(batch)

                # Process each track in the batch
                for item, features in zip(batch, audio_features_batch):
                    artist_name = item['artists'][0]['name']
                    album_name = item['album']['name']
                    popularity = item['popularity']
                    track_id = item['id']

                    # Genre (from artist)
                    try:
                        artist_info = sp.artist(item['artists'][0]['id'])
                        genres = artist_info.get('genres', [])
                        genre = genres[0] if genres else "Unknown"
                    except Exception as e:
                        print(f"Could not get genre for {artist_name}: {e}")
                        genre = "Unknown"

                    artist_id = insert_artist(artist_name)
                    album_id = insert_album(album_name, artist_id)
                    insert_song(item, album_id, genre, popularity, features)

                    total_added += 1
                    print(f"[{total_added}/100] Added: {item['name']} by {artist_name}")

                # Add delay between batches to respect rate limits
                time.sleep(1)

        except Exception as e:
            print("Error:", e)
            time.sleep(5)  # Longer delay on error

    conn.commit()
    conn.close()
    print("✅ Done. Songs inserted into the database.")

if __name__ == "__main__":
    fetch_and_store_songs(100)