import os
import sqlite3
import random
import string
import time
import requests
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env')
load_dotenv(env_path)

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

# Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET
))

# SQLite connection
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DB_PATH = os.path.join(root_dir, "Database/music_app.db")
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

def insert_song(name, album_id, genre, album_url):
    try:
        # Check if song already exists
        cur.execute("SELECT song_id FROM Song WHERE name = ? AND album_id = ?", (name, album_id))
        if cur.fetchone() is not None:
            print(f"⏭ Skipping: {name} (already exists)")
            return False
            
        cur.execute("""
        INSERT OR IGNORE INTO Song (
            name, album_id, genre, album_url
        ) VALUES (?, ?, ?, ?)""", (
            name, album_id, genre, album_url
        ))
        return True
    except Exception as e:
        print(f"Error inserting song {name}: {e}")
        return False

def get_album_cover(artist_name, track_name):
    try:
        deezer_search_url = f'https://api.deezer.com/search?q=track:"{track_name}" artist:"{artist_name}"'
        response = requests.get(deezer_search_url)
        results = response.json()
        if 'data' in results and results['data']:
            return results['data'][0]['album']['cover_medium']
    except Exception as e:
        print(f"Deezer album cover fetch failed: {e}")
    return ""

def fetch_and_store_songs(limit=100):
    total_added = 0
    seen_ids = set()

    while total_added < limit:
        try:
            query = get_random_query()
            results = sp.search(q=query, type='track', limit=50)
            for item in results['tracks']['items']:
                if total_added >= limit:
                    break
                track_id = item['id']
                if track_id in seen_ids:
                    continue
                seen_ids.add(track_id)

                track_name = item['name']
                artist_name = item['artists'][0]['name']
                album_name = item['album']['name']

                # Get genres from Spotify
                try:
                    artist_info = sp.artist(item['artists'][0]['id'])
                    genres = artist_info.get('genres', [])
                except:
                    genres = []

                if not genres:
                    print(f"⏭ Skipping: {track_name} by {artist_name} (no genre)")
                    continue  # Skip tracks without a genre

                genre = genres[0]
                album_url = get_album_cover(artist_name, track_name)

                artist_id = insert_artist(artist_name)
                album_id = insert_album(album_name, artist_id)
                if insert_song(track_name, album_id, genre, album_url):
                    total_added += 1
                    print(f"[{total_added}/{limit}] ✅ Inserted: {track_name} by {artist_name} ({genre})")

            time.sleep(1)

        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(3)

    conn.commit()
    conn.close()
    print("✅ Done. Songs inserted into the database.")

if __name__ == "__main__":
    fetch_and_store_songs(100)
