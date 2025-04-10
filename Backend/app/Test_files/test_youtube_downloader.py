import sys
import os


from app.services.youtube_downloader import YouTubeDownloader


def main():
    # Add the Backend directory to the Python path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Example YouTube URL
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Replace with your desired YouTube URL
    
    # Initialize the downloader
    downloader = YouTubeDownloader()
    
    try:
        # Download the audio
        print(f"Downloading audio from: {youtube_url}")
        audio_path = downloader.download_audio(youtube_url)
        
        if audio_path:
            print(f"Successfully downloaded audio to: {audio_path}")
            # Ask if user wants to keep the file
            response = input("Do you want to keep the downloaded file? (y/n): ").lower()
            if response != 'y':
                downloader.cleanup()
                print("Downloaded file has been deleted.")
            else:
                print(f"File kept at: {audio_path}")
        else:
            print("Failed to download audio")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        downloader.cleanup()

if __name__ == "__main__":
    main() 