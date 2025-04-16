import sys
import os
import asyncio
from typing import List

# Add the Backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.recommendation_service import RecommendationService
from app.models.song import Song, RecommendationResponse

def print_recommendations(recommendations: RecommendationResponse):
    """Helper function to print recommendation results"""
    print("\n=== Recommendations ===")
    # Print metadata
    for key, value in recommendations.metadata.items():
        if isinstance(value, dict):  # Skip printing feature weights
            continue
        print(f"{key}: {value}")
    
    print("\n=== Recommended Songs ===")
    for i, song in enumerate(recommendations.recommendations, 1):
        print(f"\n{i}. {song.title} by {song.artist}")
        print(f"   Album: {song.album}")
        print(f"   Genre: {', '.join(song.genre)}")
        print(f"   Duration: {song.duration:.2f}s")
        print(f"   Tempo: {song.tempo:.1f} BPM")
        print(f"   Spectral Centroid: {song.spectral_centroid:.2f}")
        print(f"   Zero Crossing Rate: {song.zero_crossing_rate:.2f}")
        print(f"   RMS Energy: {song.rms_energy:.2f}")

async def test_song_recommendations():
    """Test getting recommendations based on a specific song"""
    print("\n🎵 Testing Song-Based Recommendations")
    print("=====================================")
    
    service = RecommendationService()
    
    try:
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
        recommendations = await service.get_recommendations_by_song(
            song_id=song_id,
            limit=5
        )
        print_recommendations(recommendations)
        print("\n✅ Successfully got song-based recommendations")
            
    except Exception as e:
        print(f"❌ Error getting song recommendations: {str(e)}")
    finally:
        service.conn.close()

async def test_artist_recommendations():
    """Test getting recommendations based on an artist's songs"""
    print("\n👨‍🎤 Testing Artist-Based Recommendations")
    print("=======================================")
    
    service = RecommendationService()
    
    try:
        # First, find Kendrick Lamar's artist ID
        cursor = service.conn.cursor()
        cursor.execute("""
            SELECT artist_id, name
            FROM Artist
            WHERE name LIKE '%Kendrick%'
        """)
        result = cursor.fetchone()
        
        if not result:
            print("❌ Could not find Kendrick Lamar in the database")
            return
        
        artist_id = result['artist_id']
        artist_name = result['name']
        print(f"✅ Found artist: {artist_name} (ID: {artist_id})")
        
        # Get recommendations
        recommendations = await service.get_recommendations_by_artist(
            artist_id=artist_id,
            limit=5
        )
        print_recommendations(recommendations)
        print("\n✅ Successfully got artist-based recommendations")
            
    except Exception as e:
        print(f"❌ Error getting artist recommendations: {str(e)}")
    finally:
        service.conn.close()

async def run_tests():
    """Run all recommendation tests"""
    print("🎧 Starting Recommendation Service Tests")
    print("======================================")
    
    await test_song_recommendations()
    await test_artist_recommendations()
    
    print("\n🏁 Finished Running All Tests")

if __name__ == "__main__":
    asyncio.run(run_tests()) 