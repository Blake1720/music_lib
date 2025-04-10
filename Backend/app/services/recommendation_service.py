from app.models.song import Song, RecommendationResponse
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
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(root_dir, "../Database/music_app.db")
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # This enables column access by name
        self.cursor = self.conn.cursor()
        self._build_feature_tree()

    def _build_feature_tree(self):
        """Build a k-d tree of song features for efficient nearest neighbor search"""
        # Get all songs and their features
        self.cursor.execute("""
            SELECT song_id, duration, tempo, spectral_centroid, spectral_rolloff,
                   spectral_contrast, chroma_mean, chroma_std, harmonic_ratio,
                   onset_strength, zero_crossing_rate, rms_energy
            FROM Song
            WHERE duration IS NOT NULL 
              AND tempo IS NOT NULL
              AND spectral_centroid IS NOT NULL
        """)
        rows = self.cursor.fetchall()
        
        # Store song IDs for later reference
        self.song_ids = [row['song_id'] for row in rows]
        
        # Create feature matrix
        features = np.array([
            [
                row['duration'],
                row['tempo'],
                row['spectral_centroid'],
                row['spectral_rolloff'],
                row['spectral_contrast'],
                row['chroma_mean'],
                row['chroma_std'],
                row['harmonic_ratio'],
                row['onset_strength'],
                row['zero_crossing_rate'],
                row['rms_energy']
            ]
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
            tempo=row['tempo'],
            spectral_centroid=row['spectral_centroid'],
            spectral_rolloff=row['spectral_rolloff'],
            spectral_contrast=row['spectral_contrast'],
            chroma_mean=row['chroma_mean'],
            chroma_std=row['chroma_std'],
            harmonic_ratio=row['harmonic_ratio'],
            onset_strength=row['onset_strength'],
            zero_crossing_rate=row['zero_crossing_rate'],
            rms_energy=row['rms_energy']
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
            base_song.duration,
            base_song.tempo,
            base_song.spectral_centroid,
            base_song.spectral_rolloff,
            base_song.spectral_contrast,
            base_song.chroma_mean,
            base_song.chroma_std,
            base_song.harmonic_ratio,
            base_song.onset_strength,
            base_song.zero_crossing_rate,
            base_song.rms_energy
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
                    "duration": 1.0,
                    "tempo": 1.0,
                    "spectral_centroid": 1.0,
                    "spectral_rolloff": 1.0,
                    "spectral_contrast": 1.0,
                    "chroma_mean": 1.0,
                    "chroma_std": 1.0,
                    "harmonic_ratio": 1.0,
                    "onset_strength": 1.0,
                    "zero_crossing_rate": 1.0,
                    "rms_energy": 1.0
                }
            }
        )

    def __del__(self):
        """Close database connection when the service is destroyed"""
        if hasattr(self, 'conn'):
            self.conn.close() 