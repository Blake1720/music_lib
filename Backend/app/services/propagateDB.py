import os
import sqlite3
import random
import string
import time
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables
load_dotenv()
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

# Spotify authentication
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# SQLite connection
DB_PATH = "../music_app.db"
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

def insert_song(data, album_id, genre, popularity):
    # Get audio features for the track
    audio_features = sp.audio_features(data['id'])[0]
    
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
        audio_features['instrumentalness'],
        audio_features['acousticness'],
        audio_features['danceability'],
        audio_features['liveness'],
        audio_features['tempo'],
        popularity
    ))

def fetch_and_store_songs(limit=100):
    seen_ids = set()
    total_added = 0

    while total_added < limit:
        try:
            query = get_random_query()
            results = sp.search(q=query, type='track', limit=50)
            for item in results['tracks']['items']:
                if total_added >= limit:
                    break
                if item['id'] in seen_ids:
                    continue
                seen_ids.add(item['id'])

                artist_name = item['artists'][0]['name']
                album_name = item['album']['name']
                popularity = item['popularity']
                track_id = item['id']

                # Genre (from artist)
                artist_info = sp.artist(item['artists'][0]['id'])
                genres = artist_info.get('genres', [])
                genre = genres[0] if genres else "Unknown"

                artist_id = insert_artist(artist_name)
                album_id = insert_album(album_name, artist_id)
                insert_song(item, album_id, genre, popularity)

                total_added += 1
                print(f"[{total_added}/100] Added: {item['name']} by {artist_name}")
                time.sleep(0.1)  # Add a small delay to avoid rate limiting
        except Exception as e:
            print("Error:", e)
            time.sleep(1)  # Longer delay on error

    conn.commit()
    conn.close()
    print("✅ Done. Songs inserted into the database.")

if __name__ == "__main__":
    fetch_and_store_songs(100)