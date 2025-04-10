'''
This file is used to download audio from YouTube.
'''
import os
import yt_dlp
from typing import Optional

class YouTubeDownloader:
    def __init__(self, output_dir: str = "temp_audio"):
        """
        Initialize the YouTube downloader.
        
        Args:
            output_dir (str): Directory where downloaded audio files will be stored
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Configure yt-dlp options
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

    def download_audio(self, url: str) -> Optional[str]:
        """
        Download audio from a YouTube URL.
        
        Args:
            url (str): YouTube URL to download
            
        Returns:
            Optional[str]: Path to the downloaded audio file, or None if download failed
        """
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                # Get the filename of the downloaded file
                filename = ydl.prepare_filename(info)
                # Replace the extension with .mp3 since we specified mp3 as the codec
                mp3_path = os.path.splitext(filename)[0] + '.mp3'
                return mp3_path
        except Exception as e:
            print(f"Error downloading audio: {str(e)}")
            return None

    def cleanup(self):
        """Remove all downloaded audio files."""
        try:
            for file in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up files: {str(e)}") 