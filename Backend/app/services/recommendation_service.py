from app.models.song import Song, RecommendationResponse
from typing import List, Optional
import random

class RecommendationService:
    def __init__(self):
        # This would typically connect to a database or external API
        # For now, we'll use a simple in-memory storage
        self.songs = {}
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        # Sample data for demonstration
        self.songs = {
            "1": Song(
                id="1",
                title="Bohemian Rhapsody",
                artist="Queen",
                album="A Night at the Opera",
                genre=["Rock", "Progressive Rock"],
                duration=354,
                popularity=0.95
            ),
            "2": Song(
                id="2",
                title="Stairway to Heaven",
                artist="Led Zeppelin",
                album="Led Zeppelin IV",
                genre=["Rock", "Hard Rock"],
                duration=482,
                popularity=0.92
            ),
            # Add more sample songs as needed
        }

    async def get_song(self, song_id: str) -> Optional[Song]:
        return self.songs.get(song_id)

    async def get_recommendations(
        self,
        song_id: str,
        limit: int = 10,
        include_features: bool = False
    ) -> RecommendationResponse:
        # This is a simple random recommendation system
        # In a real application, this would use a proper recommendation algorithm
        base_song = await self.get_song(song_id)
        if not base_song:
            raise ValueError("Song not found")

        # Get all songs except the base song
        available_songs = [song for id, song in self.songs.items() if id != song_id]
        
        # Randomly select recommendations
        recommendations = random.sample(available_songs, min(limit, len(available_songs)))

        return RecommendationResponse(
            recommendations=recommendations,
            metadata={
                "base_song": base_song.title,
                "total_recommendations": len(recommendations),
                "algorithm": "random"  # In a real app, this would specify the actual algorithm used
            }
        ) 