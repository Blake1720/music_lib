import sys
import os
import asyncio
from typing import List

# Add the Backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.recommendation_service import RecommendationService
from app.models.song import Song

async def test_recommendations():
    # Initialize the recommendation service
    service = RecommendationService()
    
    # First, find Pride by Kendrick Lamar in the database
    cursor = service.conn.cursor()
    cursor.execute("""
        SELECT s.song_id 
        FROM Song s
        JOIN Album al ON s.album_id = al.album_id
        JOIN Artist ar ON al.artist_id = ar.artist_id
        WHERE s.name LIKE '%Pride%'
        AND ar.name LIKE '%Kendrick%'
    """)
    result = cursor.fetchone()
    
    if not result:
        print("❌ Could not find 'Pride' by Kendrick Lamar in the database")
        return
    
    song_id = str(result['song_id'])
    print(f"✅ Found 'Pride' with song_id: {song_id}")
    
    # Get recommendations
    try:
        recommendations = await service.get_recommendations(
            song_id=song_id,
            limit=10,
            include_features=True
        )
        
        print("\n=== Recommendations ===")
        print(f"Base song: {recommendations.metadata['base_song']}")
        print(f"Total recommendations: {recommendations.metadata['total_recommendations']}")
        print(f"Algorithm: {recommendations.metadata['algorithm']}")
        
        print("\n=== Recommended Songs ===")
        for i, song in enumerate(recommendations.recommendations, 1):
            print(f"\n{i}. {song.title} by {song.artist}")
            print(f"   Album: {song.album}")
            print(f"   Genre: {', '.join(song.genre)}")
            print(f"   Duration: {song.duration:.2f}s")
            print(f"   Tempo: {song.tempo:.1f} BPM")
            print(f"   Spectral Centroid: {song.spectral_centroid:.2f}")
            print(f"   Harmonic Ratio: {song.harmonic_ratio:.2f}")
            
    except Exception as e:
        print(f"❌ Error getting recommendations: {str(e)}")
    finally:
        # Clean up
        service.conn.close()

if __name__ == "__main__":
    asyncio.run(test_recommendations()) 