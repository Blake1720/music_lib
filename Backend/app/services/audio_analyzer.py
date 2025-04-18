'''
This file is used to analyze the audio files and extract features.
'''
import librosa
import numpy as np
import os
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioAnalyzer:
    def __init__(self):
        self.features = {}

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze an audio file and extract various features.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary containing all extracted features
        """
        try:
            logger.info(f"Loading audio file: {file_path}")
            y, sr = librosa.load(file_path)
            features = {}

            # 1. Basic Features
            features['duration'] = librosa.get_duration(y=y, sr=sr)
            features['tempo'], _ = librosa.beat.beat_track(y=y, sr=sr)

            # 2. Spectral Features
            features['spectral_centroid'] = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            features['spectral_rolloff'] = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
            features['spectral_contrast'] = np.mean(librosa.feature.spectral_contrast(y=y, sr=sr))

            # 3. MFCCs (Mel-Frequency Cepstral Coefficients)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            for i, mfcc in enumerate(mfccs):
                features[f'mfcc_{i+1}'] = np.mean(mfcc)

            # 4. Chroma Features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            features['chroma_mean'] = np.mean(chroma)
            features['chroma_std'] = np.std(chroma)

            # 5. Onset Strength
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            features['onset_strength'] = np.mean(onset_env)

            # 6. Zero Crossing Rate
            features['zero_crossing_rate'] = np.mean(librosa.feature.zero_crossing_rate(y))

            # 7. RMS Energy
            features['rms_energy'] = np.mean(librosa.feature.rms(y=y))

            logger.info(f"Successfully analyzed {file_path}")
            return features

        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {str(e)}")
            raise

    def analyze_directory(self, directory_path: str) -> Dict[str, Dict[str, Any]]:
        """
        Analyze all audio files in a directory.
        
        Args:
            directory_path: Path to the directory containing audio files
            
        Returns:
            Dictionary mapping filenames to their features
        """
        results = {}
        supported_formats = {'.mp3', '.wav', '.flac', '.ogg', '.m4a'}
        
        for filename in os.listdir(directory_path):
            if any(filename.lower().endswith(fmt) for fmt in supported_formats):
                file_path = os.path.join(directory_path, filename)
                try:
                    features = self.analyze_file(file_path)
                    results[filename] = features
                except Exception as e:
                    logger.error(f"Failed to analyze {filename}: {str(e)}")
        
        return results

if __name__ == "__main__":
    analyzer = AudioAnalyzer()

    # Example usage:
    # features = analyzer.analyze_file("path/to/audio.wav")
    # print(features)

    # results = analyzer.analyze_directory("path/to/directory")
    # print(results)
