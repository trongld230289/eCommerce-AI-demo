#!/usr/bin/env python3
"""
Voice Search Test Script
This script demonstrates how to use the voice search API endpoint.
"""

import requests
import json
import os
from pathlib import Path

def test_voice_search(audio_file_path: str, limit: int = 5):
    """Test the voice search API with an audio file"""
    
    # Check if audio file exists
    if not os.path.exists(audio_file_path):
        print(f"❌ Audio file not found: {audio_file_path}")
        return False
    
    print(f"🎤 Testing voice search with: {audio_file_path}")
    
    try:
        # Prepare the audio file for upload
        with open(audio_file_path, 'rb') as audio_file:
            files = {
                'audio': (os.path.basename(audio_file_path), audio_file, 'audio/wav')
            }
            params = {
                'limit': limit
            }
            
            # Send request to voice search endpoint
            response = requests.post(
                'http://localhost:8000/api/ai/search-by-voice',
                files=files,
                params=params
            )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Voice search successful!")
            print(f"📝 Transcribed text: '{result.get('transcribed_text', 'N/A')}'")
            print(f"🔍 Search intent: {result.get('search_intent', 'N/A')}")
            print(f"📊 Total results: {result.get('total_results', 0)}")
            
            if result.get('products'):
                print("\n🛍️ Products found:")
                for product in result['products'][:3]:  # Show top 3
                    print(f"  - {product['name']} - ${product['price']} (similarity: {product.get('similarity_score', 'N/A'):.3f})")
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to backend server on localhost:8000")
        print("Please make sure the backend server is running.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_transcription_only(audio_file_path: str):
    """Test just the transcription API"""
    
    if not os.path.exists(audio_file_path):
        print(f"❌ Audio file not found: {audio_file_path}")
        return False
    
    print(f"🎤 Testing transcription with: {audio_file_path}")
    
    try:
        with open(audio_file_path, 'rb') as audio_file:
            files = {
                'audio': (os.path.basename(audio_file_path), audio_file, 'audio/wav')
            }
            
            response = requests.post(
                'http://localhost:8000/api/ai/transcribe',
                files=files
            )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Transcription successful!")
            print(f"📝 Transcribed text: '{result.get('text', 'N/A')}'")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎤 Voice Search API Test")
    print("=" * 50)
    
    # Example usage - replace with your actual audio file path
    audio_file = "test_audio.wav"  # You need to provide an actual audio file
    
    if os.path.exists(audio_file):
        print("\n1. Testing transcription only...")
        test_transcription_only(audio_file)
        
        print("\n2. Testing full voice search...")
        test_voice_search(audio_file)
    else:
        print(f"\n📁 Please create or provide an audio file at: {audio_file}")
        print("You can record yourself saying something like:")
        print("  - 'I want a laptop under 1200 dollars'")
        print("  - 'Show me phones under 500'")
        print("  - 'Find me gaming headphones'")
        print("\nSupported formats: wav, mp3, m4a, flac")
        print("Maximum file size: 25MB")
        
        print("\n💡 To test the API manually, you can use curl:")
        print("curl -X POST 'http://localhost:8000/api/ai/search-by-voice' \\")
        print("     -F 'audio=@your_audio_file.wav' \\")
        print("     -F 'limit=5'")
