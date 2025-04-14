'''
This file is used to populate the database with data from Spotify.
'''
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

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# SQLite connection
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DB_PATH = os.path.join(root_dir, "Database/music_app.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

def get_random_query():
    # Mix of lowercase letters and digits, 2-character queries
    charset = string.ascii_lowercase + string.digits
    return ''.join(random.choices(charset, k=2))

def insert_artist(name):
    cur.execute("INSERT OR IGNORE INTO Artist (name) VALUES (?)", (name,))
    cur.execute("SELECT artist_id FROM Artist WHERE name = ?", (name,))
    return cur.fetchone()[0]

def insert_album(name, artist_id, album_url):
    cur.execute("INSERT OR IGNORE INTO Album (name, artist_id, date_created, album_url) VALUES (?, ?, datetime('now'), ?)", 
                (name, artist_id, album_url))
    cur.execute("SELECT album_id FROM Album WHERE name = ? AND artist_id = ?", (name, artist_id))
    return cur.fetchone()[0]

def insert_song(name, album_id, genre):
    try:
        cur.execute("SELECT song_id FROM Song WHERE name = ? AND album_id = ?", (name, album_id))
        if cur.fetchone() is not None:
            print(f"⏭ Skipping: {name} (already exists)")
            return False
            
        cur.execute("""
        INSERT OR IGNORE INTO Song (
            name, album_id, genre
        ) VALUES (?, ?, ?)""", (
            name, album_id, genre
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
            print(f"\n🔎 Searching Spotify with query: '{query}'")
            results = sp.search(q=query, type='track', limit=50)

            for item in results.get('tracks', {}).get('items', []):
                if total_added >= limit:
                    break

                track_id = item.get('id')
                if not track_id or track_id in seen_ids:
                    continue
                seen_ids.add(track_id)

                try:
                    track_name = item.get('name')
                    artist_info = item.get('artists')
                    album_info = item.get('album')

                    if not track_name or not artist_info or not album_info:
                        print("⏭ Skipping track due to missing metadata.")
                        continue

                    artist_name = artist_info[0].get('name') if artist_info and len(artist_info) > 0 else None
                    album_name = album_info.get('name')

                    if not artist_name or not album_name:
                        print(f"⏭ Skipping track '{track_name}' due to incomplete artist/album data.")
                        continue

                except Exception as e:
                    print(f"⏭ Skipping track due to unexpected structure: {e}")
                    continue

                # Get genre
                try:
                    artist_data = sp.artist(artist_info[0]['id'])
                    genres = artist_data.get('genres', [])
                except:
                    genres = []

                if not genres:
                    print(f"⏭ Skipping: {track_name} by {artist_name} (no genre)")
                    continue

                genre = genres[0]

                # Get album cover
                album_url = get_album_cover(artist_name, track_name)
                if not album_url:
                    print(f"⏭ Skipping: {track_name} by {artist_name} (no album cover)")
                    continue

                # Insert artist and album
                artist_id = insert_artist(artist_name)
                album_id = insert_album(album_name, artist_id, album_url)

                if insert_song(track_name, album_id, genre):
                    total_added += 1
                    print(f"[{total_added}/{limit}] ✅ Inserted: {track_name} by {artist_name} ({genre})")

            time.sleep(1)

        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(3)

    conn.commit()
    conn.close()
    print("\n✅ Done. Songs inserted into the database.")

if __name__ == "__main__":
    fetch_and_store_songs(200)