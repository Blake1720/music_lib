import sys
import os

from services.audio_analyzer import AudioAnalyzer
import json
import numpy as np

def format_value(value):
    if isinstance(value, np.ndarray):
        return float(np.mean(value))  # Convert to float
    return float(value) if isinstance(value, np.number) else value

def main():
    # Initialize the analyzer
    analyzer = AudioAnalyzer()
    
    # Analyze the sample file
    features = analyzer.analyze_file("test_audio/sample.mp3")
    
    # Print the features in a readable format
    print("\nExtracted Audio Features:")
    print("=" * 50)
    for feature, value in features.items():
        formatted_value = format_value(value)
        if isinstance(formatted_value, float):
            print(f"{feature}: {formatted_value:.4f}")
        else:
            print(f"{feature}: {formatted_value}")
    
    # Save features to a JSON file
    with open("audio_features.json", "w") as f:
        # Convert all values to Python native types
        json_features = {k: format_value(v) for k, v in features.items()}
        json.dump(json_features, f, indent=4)
    print("\nFeatures saved to audio_features.json")

if __name__ == "__main__":
    main() 