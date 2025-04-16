'''
This service handles importing songs from Spotify links into our database.
'''
import re
import sqlite3
import os
import time
import yt_dlp
from typing import Optional, Dict
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from app.services.audio_analyzer import AudioAnalyzer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpotifyImportService:
    def __init__(self, temp_dir: str = "temp_audio"):
        """
        Initialize the Spotify import service.
        
        Args:
            temp_dir: Directory for temporary audio files
        """
        # Initialize Spotify client
        try:
            self.spotify = spotipy.Spotify(
                client_credentials_manager=SpotifyClientCredentials()
            )
        except Exception as e:
            logger.error(f"Failed to initialize Spotify client: {e}")
            raise ValueError("Failed to initialize Spotify client. Check your credentials.")
        
        # Get root directory and set up absolute paths
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.temp_dir = os.path.abspath(os.path.join(self.root_dir, temp_dir))
        
        # Create temp directory
        os.makedirs(self.temp_dir, exist_ok=True)
        logger.info(f"Created temp directory at: {self.temp_dir}")
        
        # Connect to the database
        db_path = os.path.join(self.root_dir, "../Database/music_app.db")
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        # Initialize audio analyzer
        self.audio_analyzer = AudioAnalyzer()

    def _extract_spotify_id(self, spotify_url: str) -> Optional[str]:
        """Extract the Spotify track ID from a Spotify URL"""
        # Match patterns like: https://open.spotify.com/track/1234567890
        match = re.search(r'track/([a-zA-Z0-9]+)', spotify_url)
        return match.group(1) if match else None

    def _get_or_create_artist(self, artist_name: str) -> int:
        """Get artist ID from database or create if not exists"""
        self.cursor.execute(
            "SELECT artist_id FROM Artist WHERE name = ?",
            (artist_name,)
        )
        result = self.cursor.fetchone()
        
        if result:
            return result['artist_id']
            
        self.cursor.execute(
            "INSERT INTO Artist (name) VALUES (?)",
            (artist_name,)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def _get_or_create_album(self, album_name: str, artist_id: int, album_url: str = None) -> int:
        """Get album ID from database or create if not exists"""
        self.cursor.execute(
            "SELECT album_id FROM Album WHERE name = ? AND artist_id = ?",
            (album_name, artist_id)
        )
        result = self.cursor.fetchone()
        
        if result:
            return result['album_id']
            
        # Use default album cover if none provided
        if not album_url:
            album_url = "/Backend/public/album_cover.jpg"
            
        self.cursor.execute(
            "INSERT INTO Album (name, artist_id, album_url) VALUES (?, ?, ?)",
            (album_name, artist_id, album_url)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def _song_exists(self, name: str, album_id: int) -> bool:
        """Check if song already exists in database"""
        self.cursor.execute(
            "SELECT 1 FROM Song WHERE name = ? AND album_id = ?",
            (name, album_id)
        )
        return bool(self.cursor.fetchone())

    def _get_youtube_url(self, song_name: str, artist_name: str) -> Optional[str]:
        """Get YouTube URL for a song"""
        search_query = f"{song_name} {artist_name} Audio"
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'default_search': 'ytsearch',
            'nocheckcertificate': True,
            'ignoreerrors': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{search_query}", download=False)
                if not info['entries']:
                    logger.error(f"No results found for: {search_query}")
                    return None
                return f"https://www.youtube.com/watch?v={info['entries'][0]['id']}"
        except Exception as e:
            logger.error(f"Error searching for {search_query}: {e}")
            return None

    def _download_audio(self, url: str, output_path: str) -> bool:
        """Download audio from YouTube URL"""
        max_retries = 3
        retry_delay = 5
        for attempt in range(max_retries):
            try:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': output_path,
                    'quiet': True,
                    'no_warnings': True
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                return True
            except Exception as e:
                logger.error(f"Download attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"Failed to download after {max_retries} attempts")
                    return False
        return False

    def import_song(self, spotify_url: str) -> Dict:
        """Import a song from Spotify URL into our database"""
        # Extract Spotify ID
        track_id = self._extract_spotify_id(spotify_url)
        if not track_id:
            raise ValueError("Invalid Spotify URL format")

        try:
            # Get track info from Spotify
            track = self.spotify.track(track_id)
            if not track:
                raise ValueError("Track not found on Spotify")

            # Extract basic info
            song_name = track['name']
            artist_name = track['artists'][0]['name']
            album_name = track['album']['name']
            album_url = track['album']['images'][0]['url'] if track['album']['images'] else "/Backend/public/album_cover.jpg"
            
            logger.info(f"Processing: {song_name} by {artist_name}")
            
            # Get or create artist and album
            artist_id = self._get_or_create_artist(artist_name)
            album_id = self._get_or_create_album(album_name, artist_id, album_url)
            
            # Check if song already exists
            if self._song_exists(song_name, album_id):
                return {
                    "status": "exists",
                    "message": f"Song '{song_name}' by {artist_name} already exists in database",
                    "song_details": {
                        "name": song_name,
                        "artist": artist_name,
                        "album": album_name
                    }
                }

            # Get YouTube URL and download
            video_url = self._get_youtube_url(song_name, artist_name)
            if not video_url:
                raise ValueError(f"Could not find YouTube video for: {song_name} by {artist_name}")

            # Download audio
            output_path = os.path.join(self.temp_dir, f"{song_name} {artist_name}")
            logger.info(f"Downloading audio to: {output_path}")
            
            if not self._download_audio(video_url, output_path):
                raise ValueError(f"Failed to download audio for: {song_name}")

            audio_path = f"{output_path}.mp3"
            if not os.path.exists(audio_path):
                raise ValueError(f"Downloaded audio file not found: {audio_path}")

            try:
                # Analyze audio features
                logger.info(f"Analyzing audio file: {audio_path}")
                features = self.audio_analyzer.analyze_file(audio_path)
                
                # Get genre from Spotify artist
                try:
                    artist_data = self.spotify.artist(track['artists'][0]['id'])
                    genre = artist_data['genres'][0] if artist_data['genres'] else None
                except:
                    genre = None
                
                # Insert into database
                self.cursor.execute("""
                    INSERT INTO Song (
                        name, album_id, duration, tempo, spectral_centroid,
                        spectral_rolloff, spectral_contrast, chroma_mean,
                        chroma_std, onset_strength, zero_crossing_rate,
                        rms_energy, genre
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    song_name, album_id, features['duration'], features['tempo'],
                    features['spectral_centroid'], features['spectral_rolloff'],
                    features['spectral_contrast'], features['chroma_mean'],
                    features['chroma_std'], features['onset_strength'],
                    features['zero_crossing_rate'], features['rms_energy'],
                    genre  # Can be None if no genre found
                ))
                self.conn.commit()
                
                logger.info(f"Successfully imported: {song_name}")
                return {
                    "status": "success",
                    "message": f"Successfully imported '{song_name}' by {artist_name}",
                    "song_details": {
                        "name": song_name,
                        "artist": artist_name,
                        "album": album_name,
                        "genre": genre,
                        "features": features
                    }
                }
            finally:
                # Clean up the downloaded file
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                    logger.info(f"Cleaned up temporary file: {audio_path}")
        
        except spotipy.exceptions.SpotifyException as e:
            raise ValueError(f"Spotify API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error importing song: {str(e)}")
            raise

    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'conn'):
            self.conn.close()
        # Clean up temp directory
        if os.path.exists(self.temp_dir):
            try:
                for file in os.listdir(self.temp_dir):
                    file_path = os.path.join(self.temp_dir, file)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                os.rmdir(self.temp_dir)
                logger.info(f"Cleaned up temp directory: {self.temp_dir}")
            except Exception as e:
                logger.error(f"Error cleaning up temp directory: {e}")

    def __del__(self):
        """Cleanup when the object is destroyed"""
        self.cleanup() 