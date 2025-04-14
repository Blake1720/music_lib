# Music Library

# Setup

1. Create a .env file and add your API keys
2. Start the virtual environment with `python -m venv venv`
3. (mac) Activate the virtual environment with `source venv/bin/activate`
3. (windows) Activate the virtual environment with `venv\Scripts\activate`
4. Install the dependencies with `pip install -r requirements.txt`
5. Download FFEMPEG -- Required for audio analysis
    * Install FFmpeg:
      * macOS: `brew install ffmpeg`
      * Windows: Download from https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
        - Unzip the file
        - Add the `bin` directory of your FFmpeg installation to your system PATH
        - Example: `C:\ffmpeg\bin`
6. Run the app with `uvicorn main:app --reload`

# Database

1. Run `python Database/create_database.py` to create the database
2. Run `python Backend/app/services/propagateDB.py` to populate the database
3. Run `python Backend/app/services/analyze_songs.py` to analyze the songs and add features to the database

# Test files

1. Run 'python -m app.Test_files.test_recommendations' to test the recommendations
2. Run 'python -m app.Test_files.test_youtube_downloader' to test the youtube downloader
3. Run 'python -m app.Test_files.test_audio_analysis' to test the audio analysis

# Frontend
1. Download Node.js -- Required for frontend development
    * Install Node.js:
      * macOS: `brew install node`
      * Windows: Download from https://nodejs.org/en/download
      – Run the installer
      – Follow the setup wizard (use default settings)
      – Ensure the box for npm (Node Package Manager) is checked
2. Run `npm install` to install dependencies
3. Run `npm start dev` to start the server

![image](https://github.com/user-attachments/assets/7e85cdcb-10f2-46fa-824f-7a4c41eb902b)
