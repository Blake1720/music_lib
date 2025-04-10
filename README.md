# Music Library

Right now I have the basic framework setup for the db. Run queries inside of query.py. #Where the comment says to
The Schema is not correct yet.

# Setup

1. Create a .env file and add your API keys
2. Start the virtual environment with `python -m venv venv`
3. (mac) Activate the virtual environment with `source venv/bin/activate`
3. (windows) Activate the virtual environment with `venv\Scripts\activate`
4. Install the dependencies with `pip install -r requirements.txt`
5. Run the app with `uvicorn main:app --reload`

# Database

1. Run `python Database/create_database.py` to create the database
2. Run `python Database/insert_data.py` to insert the data into the database

# Test files

1. Run 'python -m app.Test_files.test_recommendations' to test the recommendations
2. Run 'python -m app.Test_files.test_youtube_downloader' to test the youtube downloader
3. Run 'python -m app.Test_files.test_audio_analysis' to test the audio analysis
