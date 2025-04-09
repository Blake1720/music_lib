from models.song import Song, RecommendationResponse
from typing import List, Optional, Tuple
import random
import sqlite3
import os
from datetime import datetime
import numpy as np
from scipy.spatial import cKDTree

class RecommendationService:
    def __init__(self):
        # Connect to the SQLite database
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                              "Database", "music_app.db")
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # This enables column access by name
        self.cursor = self.conn.cursor()
        self._build_feature_tree()

    def _build_feature_tree(self):
        """Build a k-d tree of song features for efficient nearest neighbor search"""
        # Get all songs and their features
        self.cursor.execute("""
            SELECT song_id, popularity, instrumentalness, acousticness, 
                   danceability, liveness, tempo 
            FROM Song
        """)
        rows = self.cursor.fetchall()
        
        # Store song IDs for later reference
        self.song_ids = [row['song_id'] for row in rows]
        
        # Create feature matrix
        features = np.array([
            [row['popularity'], row['instrumentalness'], row['acousticness'],
             row['danceability'], row['liveness'], row['tempo']]
            for row in rows
        ])
        
        # Normalize features to [0,1] range
        self.feature_min = features.min(axis=0)
        self.feature_max = features.max(axis=0)
        normalized_features = (features - self.feature_min) / (self.feature_max - self.feature_min)
        
        # Build k-d tree
        self.feature_tree = cKDTree(normalized_features)

    def _normalize_features(self, features: List[float]) -> np.ndarray:
        """Normalize a single song's features"""
        return (np.array(features) - self.feature_min) / (self.feature_max - self.feature_min)

    def _get_song_from_row(self, row) -> Song:
        """Convert a database row to a Song object"""
        return Song(
            id=str(row['song_id']),
            title=row['name'],
            artist=self._get_artist_name(row['album_id']),
            album=self._get_album_name(row['album_id']),
            genre=row['genre'].split(',') if row['genre'] else [],
            duration=row['duration'],
            popularity=row['popularity'],
            instrumentalness=row['instrumentalness'],
            acousticness=row['acousticness'],
            danceability=row['danceability'],
            liveness=row['liveness'],
            tempo=row['tempo']
        )

    def _get_artist_name(self, album_id: int) -> str:
        """Get artist name for an album"""
        self.cursor.execute("""
            SELECT a.name 
            FROM Artist a
            JOIN Album al ON a.artist_id = al.artist_id
            WHERE al.album_id = ?
        """, (album_id,))
        result = self.cursor.fetchone()
        return result['name'] if result else "Unknown Artist"

    def _get_album_name(self, album_id: int) -> str:
        """Get album name"""
        self.cursor.execute("""
            SELECT name 
            FROM Album 
            WHERE album_id = ?
        """, (album_id,))
        result = self.cursor.fetchone()
        return result['name'] if result else "Unknown Album"

    async def get_song(self, song_id: str) -> Optional[Song]:
        self.cursor.execute("""
            SELECT * FROM Song WHERE song_id = ?
        """, (song_id,))
        row = self.cursor.fetchone()
        return self._get_song_from_row(row) if row else None

    async def get_recommendations(
        self,
        song_id: str,
        limit: int = 10,
        include_features: bool = False
    ) -> RecommendationResponse:
        # Get the base song
        base_song = await self.get_song(song_id)
        if not base_song:
            raise ValueError("Song not found")

        # Get the index of the base song in our feature tree
        base_song_idx = self.song_ids.index(int(song_id))
        
        # Get the base song's features and normalize them
        base_features = [
            base_song.popularity,
            base_song.instrumentalness,
            base_song.acousticness,
            base_song.danceability,
            base_song.liveness,
            base_song.tempo
        ]
        normalized_features = self._normalize_features(base_features)
        
        # Query the k-d tree for nearest neighbors
        # We query for limit+1 because the closest match will be the song itself
        distances, indices = self.feature_tree.query(
            normalized_features,
            k=limit+1,
            p=2  # Euclidean distance
        )
        
        # Remove the base song from results (it's the closest match to itself)
        indices = indices[1:]  # Skip the first result (self)
        
        # Get the recommended songs
        recommended_song_ids = [self.song_ids[idx] for idx in indices]
        recommendations = []
        
        for rec_id in recommended_song_ids:
            self.cursor.execute("""
                SELECT * FROM Song WHERE song_id = ?
            """, (rec_id,))
            row = self.cursor.fetchone()
            if row:
                recommendations.append(self._get_song_from_row(row))

        return RecommendationResponse(
            recommendations=recommendations,
            metadata={
                "base_song": base_song.title,
                "total_recommendations": len(recommendations),
                "algorithm": "k-d tree nearest neighbors",
                "feature_weights": {
                    "popularity": 1.0,
                    "instrumentalness": 1.0,
                    "acousticness": 1.0,
                    "danceability": 1.0,
                    "liveness": 1.0,
                    "tempo": 1.0
                }
            }
        )

    def __del__(self):
        """Close database connection when the service is destroyed"""
        if hasattr(self, 'conn'):
            self.conn.close() 