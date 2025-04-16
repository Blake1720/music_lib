import sys
import os
import logging
from typing import Dict
import numpy as np

# Add the Backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(backend_dir)

from app.services.spotify_import_service import SpotifyImportService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_feature_value(value) -> float:
    """Helper function to convert numpy values to Python floats"""
    if isinstance(value, np.ndarray):
        return float(value[0]) if value.size > 0 else 0.0
    return float(value) if value is not None else 0.0

def print_import_result(result: Dict):
    """Helper function to print import results in a readable format"""
    print("\n=== Import Result ===")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    
    if result.get('song_details'):
        print("\n=== Song Details ===")
        details = result['song_details']
        print(f"Name: {details['name']}")
        print(f"Artist: {details['artist']}")
        print(f"Album: {details['album']}")
        
        if 'features' in details:
            print("\n=== Audio Features ===")
            features = details['features']
            print(f"Duration: {format_feature_value(features['duration']):.2f}s")
            print(f"Tempo: {format_feature_value(features['tempo']):.1f} BPM")
            print(f"Spectral Centroid: {format_feature_value(features['spectral_centroid']):.2f}")
            print(f"Spectral Rolloff: {format_feature_value(features['spectral_rolloff']):.2f}")
            print(f"Spectral Contrast: {format_feature_value(features['spectral_contrast']):.2f}")
            print(f"Chroma Mean: {format_feature_value(features['chroma_mean']):.2f}")
            print(f"Chroma Std: {format_feature_value(features['chroma_std']):.2f}")
            print(f"Onset Strength: {format_feature_value(features['onset_strength']):.2f}")
            print(f"Zero Crossing Rate: {format_feature_value(features['zero_crossing_rate']):.4f}")
            print(f"RMS Energy: {format_feature_value(features['rms_energy']):.6f}")

def test_spotify_import():
    """Test importing a song from Spotify"""
    print("🎵 Testing Spotify Song Import")
    print("=============================")
    
    service = None
    try:
        # Create service with test-specific temp directory
        temp_dir = os.path.join(backend_dir, "test_temp_audio")
        service = SpotifyImportService(temp_dir=temp_dir)
        
        # Test with "Attack" by Thirty Seconds To Mars
        spotify_url = "https://open.spotify.com/track/0lHSJ0ZP8uUPnJXhMdGjOK"
        print(f"\nTesting import of track: {spotify_url}")
        
        # First import - should succeed
        print("\n1. Testing first-time import (should succeed):")
        result = service.import_song(spotify_url)
        print_import_result(result)
        
        # Second import - should detect duplicate
        print("\n2. Testing duplicate import (should detect existing song):")
        result = service.import_song(spotify_url)
        print_import_result(result)
        
        print("\n✅ Spotify import tests completed successfully")
            
    except ValueError as e:
        print(f"\n❌ Validation error during Spotify import test: {str(e)}")
    except Exception as e:
        print(f"\n❌ Unexpected error during Spotify import test: {str(e)}")
    finally:
        # Clean up
        if service:
            service.cleanup()

def test_invalid_url():
    """Test handling of invalid Spotify URLs"""
    print("\n🔍 Testing Invalid URL Handling")
    print("==============================")
    
    service = None
    try:
        # Create service with test-specific temp directory
        temp_dir = os.path.join(backend_dir, "test_temp_audio")
        service = SpotifyImportService(temp_dir=temp_dir)
        
        # Test with invalid URL
        invalid_url = "https://open.spotify.com/track/invalid"
        print(f"\nTesting import with invalid URL: {invalid_url}")
        
        result = service.import_song(invalid_url)
        print_import_result(result)
        
    except ValueError as e:
        print(f"\n✅ Successfully caught invalid URL error: {str(e)}")
    except Exception as e:
        print(f"\n❌ Unexpected error during invalid URL test: {str(e)}")
    finally:
        if service:
            service.cleanup()

def run_tests():
    """Run all Spotify import tests"""
    print("🎧 Starting Spotify Import Service Tests")
    print("=======================================")
    
    test_spotify_import()
    test_invalid_url()
    
    print("\n🏁 All Spotify Import Tests Completed")

if __name__ == "__main__":
    run_tests() 