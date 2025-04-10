'''
This file is used to analyze the songs and add features to the database.
'''
import os
import sqlite3
import time
import yt_dlp
from typing import Optional
import numpy as np

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.sys.path.append(project_root)

from Backend.app.services.youtube_downloader import YouTubeDownloader
from Backend.app.services.audio_analyzer import AudioAnalyzer

# Get database connection
DB_PATH = os.path.join(project_root, "Database/music_app.db")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

def get_youtube_url(song_name: str, artist_name: str) -> Optional[str]:
    """Search for a song on YouTube and return the URL"""
    search_query = f"{song_name} {artist_name} Audio"
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'default_search': 'ytsearch',
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{search_query}", download=False)
            if not info['entries']:
                print(f"❌ No results found for: {search_query}")
                return None
            return f"https://www.youtube.com/watch?v={info['entries'][0]['id']}"
    except Exception as e:
        print(f"❌ Error searching for {search_query}: {e}")
        return None

def update_song_features(song_id: int, features: dict):
    """Update song features in the database"""
    try:
        # Print features for debugging
        print("Available features:", list(features.keys()))
        
        # Convert numpy arrays to bytes for storage if they exist
        mel_spectrogram_bytes = features.get('mel_spectrogram', np.array([])).tobytes() if 'mel_spectrogram' in features else None
        tonnetz_bytes = features.get('tonnetz', np.array([])).tobytes() if 'tonnetz' in features else None
        
        # Helper function to safely convert numpy arrays to float
        def safe_float(value, default=0):
            if isinstance(value, np.ndarray):
                if value.size > 0:
                    return float(value[0])  # Take first value for single values
                return default
            return float(value) if value is not None else default
        
        # Get all features with proper array handling
        duration = safe_float(features.get('duration', 0))
        tempo = safe_float(features.get('tempo', 0))
        spectral_centroid = safe_float(features.get('spectral_centroid', 0))
        spectral_rolloff = safe_float(features.get('spectral_rolloff', 0))
        spectral_contrast = safe_float(features.get('spectral_contrast', 0))
        chroma_mean = safe_float(features.get('chroma_mean', 0))
        chroma_std = safe_float(features.get('chroma_std', 0))
        harmonic_ratio = safe_float(features.get('harmonic_ratio', 0))
        onset_strength = safe_float(features.get('onset_strength', 0))
        zero_crossing_rate = safe_float(features.get('zero_crossing_rate', 0))
        rms_energy = safe_float(features.get('rms_energy', 0))
        
        cur.execute("""
            UPDATE Song SET
                duration = ?,
                tempo = ?,
                spectral_centroid = ?,
                spectral_rolloff = ?,
                spectral_contrast = ?,
                chroma_mean = ?,
                chroma_std = ?,
                harmonic_ratio = ?,
                onset_strength = ?,
                zero_crossing_rate = ?,
                rms_energy = ?,
                mel_spectrogram = ?,
                tonnetz = ?
            WHERE song_id = ?
        """, (
            duration,
            tempo,
            spectral_centroid,
            spectral_rolloff,
            spectral_contrast,
            chroma_mean,
            chroma_std,
            harmonic_ratio,
            onset_strength,
            zero_crossing_rate,
            rms_energy,
            mel_spectrogram_bytes,
            tonnetz_bytes,
            song_id
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Error updating features for song_id {song_id}: {e}")
        print("Features dictionary:", features)
        return False

def download_audio(url: str, output_path: str) -> bool:
    """Download audio from YouTube URL with retry logic"""
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }],
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'force_generic_extractor': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return True
            
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"Failed to download after {max_retries} attempts")
                return False
    
    return False

def process_songs():
    """Process all songs in the database that don't have features yet"""
    # Initialize downloader and analyzer
    downloader = YouTubeDownloader()
    analyzer = AudioAnalyzer()
    
    cur.execute("""
        SELECT s.song_id, s.name, a.name as artist_name
        FROM Song s
        JOIN Album al ON s.album_id = al.album_id
        JOIN Artist a ON al.artist_id = a.artist_id
        WHERE s.duration IS NULL
    """)
    songs = cur.fetchall()
    
    total = len(songs)
    print(f"\nFound {total} songs to process")
    
    for i, song in enumerate(songs, 1):
        song_id, song_name, artist_name = song
        print(f"\n[{i}/{total}] Processing: {song_name} by {artist_name}")
        
        try:
            # Get YouTube URL
            video_url = get_youtube_url(song_name, artist_name)
            if not video_url:
                continue
                
            # Download audio
            audio_path = downloader.download_audio(video_url)
            if not audio_path:
                continue
                
            try:
                # Analyze audio
                features = analyzer.analyze_file(audio_path)
                if features:
                    # Update database
                    if update_song_features(song_id, features):
                        print(f"✅ Successfully updated features for {song_name}")
                    else:
                        print(f"❌ Failed to update features for {song_name}")
            finally:
                # Clean up downloaded file
                try:
                    os.remove(audio_path)
                except:
                    pass
                
        except Exception as e:
            print(f"❌ Error processing {song_name}: {e}")
            continue
            
        # Sleep to avoid rate limiting
        time.sleep(2)
    
    # Clean up
    downloader.cleanup()
    conn.close()
    print("\n✅ Finished processing all songs")

if __name__ == "__main__":
    process_songs() 