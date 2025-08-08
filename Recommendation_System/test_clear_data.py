#!/usr/bin/env python3
"""
Test script to demonstrate the clear_all_data.py functionality
This creates some test data and then clears it
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clear_all_data import RecommendationSystemDataCleaner

def create_test_data():
    """Create some test data in Chroma DB"""
    try:
        import chromadb
        client = chromadb.PersistentClient(path="./test_chroma_db")
        
        # Create test collection
        collection = client.get_or_create_collection("test_collection")
        
        # Add test data
        collection.add(
            documents=["test document 1", "test document 2"],
            metadatas=[{"type": "test"}, {"type": "test"}],
            ids=["test1", "test2"]
        )
        
        print("✅ Created test data in test_chroma_db")
        return True
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        return False

def test_cleanup():
    """Test the cleanup functionality"""
    print("🧪 Testing Recommendation System Data Cleaner")
    print("=" * 50)
    
    # Create test data
    create_test_data()
    
    # Test the cleaner with test database
    cleaner = RecommendationSystemDataCleaner(chroma_db_path="./test_chroma_db")
    
    # Show collections before cleanup
    print("\n📋 Collections before cleanup:")
    collections = cleaner.list_collections()
    
    # Perform cleanup
    print("\n🧹 Performing cleanup...")
    success = cleaner.clear_all_recommendation_data()
    
    # Show results
    print(f"\n📊 Cleanup result: {'Success' if success else 'Failed'}")
    
    # Cleanup test directory
    import shutil
    try:
        shutil.rmtree("./test_chroma_db")
        print("🧹 Cleaned up test directory")
    except Exception as e:
        print(f"⚠️  Could not clean test directory: {e}")

if __name__ == "__main__":
    test_cleanup()
