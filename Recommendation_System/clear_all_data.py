#!/usr/bin/env python3
"""
Clear Recommendation System Data Script
======================================
This script clears data from:
1. Chroma DB Vector Database (user_events and product_embeddings collections)
2. Vector database files
3. Cache files

Use with caution - this will delete all recommendation system data!
Note: This script handles ONLY Recommendation System / Vector Database operations
"""

import os
import sys
import shutil
from typing import Optional, List, Dict
from dotenv import load_dotenv

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Try to import Chroma DB
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    print("⚠️  Chroma DB not available")
    CHROMA_AVAILABLE = False


class RecommendationSystemDataCleaner:
    """
    Data cleaner for Recommendation System Vector Database and Cache
    Handles Chroma DB collections, vector files, and cache cleanup
    """
    
    def __init__(self, chroma_db_path: Optional[str] = None):
        self.chroma_db_path = chroma_db_path or "./chroma_db"
        self.chroma_client = None
        
        # Known collection names from the system
        self.collection_names = [
            "user_events",           # User interaction events
            "product_embeddings",    # Product vector embeddings  
            "event_embeddings",      # Additional event embeddings
            "semantic_search",       # Semantic search data
            "recommendations"        # Recommendation cache
        ]
        
        # Initialize Chroma DB client
        if CHROMA_AVAILABLE:
            try:
                if os.path.exists(self.chroma_db_path):
                    self.chroma_client = chromadb.PersistentClient(path=self.chroma_db_path)
                    print(f"✅ Chroma DB client initialized at: {self.chroma_db_path}")
                else:
                    print(f"⚠️  Chroma DB path does not exist: {self.chroma_db_path}")
            except Exception as e:
                print(f"❌ Failed to initialize Chroma DB: {e}")
                self.chroma_client = None
        else:
            print("❌ Chroma DB not available")

    def list_collections(self) -> List[str]:
        """List all existing collections in Chroma DB"""
        if not self.chroma_client:
            print("❌ Chroma DB client not available")
            return []
        
        try:
            # Try new API first (v0.6.0+)
            try:
                collections = self.chroma_client.list_collections()
                # In v0.6.0+, list_collections returns collection names directly
                if collections and isinstance(collections[0], str):
                    collection_names = collections
                else:
                    # Older version - collections have .name attribute
                    collection_names = [col.name for col in collections]
            except Exception:
                # Fallback: try to get known collections
                collection_names = []
                for name in self.collection_names:
                    try:
                        self.chroma_client.get_collection(name)
                        collection_names.append(name)
                    except Exception:
                        pass
            
            print(f"📋 Found {len(collection_names)} collections: {collection_names}")
            return collection_names
        except Exception as e:
            print(f"❌ Error listing collections: {e}")
            # Try to get known collections individually
            collection_names = []
            for name in self.collection_names:
                try:
                    self.chroma_client.get_collection(name)
                    collection_names.append(name)
                    print(f"   Found collection: {name}")
                except Exception:
                    pass
            return collection_names

    def clear_collection(self, collection_name: str) -> bool:
        """Clear a specific Chroma DB collection"""
        if not self.chroma_client:
            print(f"❌ Chroma DB client not available for collection: {collection_name}")
            return False
        
        try:
            print(f"🧹 Clearing collection: {collection_name}")
            
            # Get collection
            try:
                collection = self.chroma_client.get_collection(collection_name)
            except Exception:
                print(f"   Collection '{collection_name}' does not exist, skipping...")
                return True
            
            # Get all items in collection
            try:
                result = collection.get()
                item_count = len(result['ids']) if result and 'ids' in result else 0
                
                if item_count > 0:
                    # Delete all items in batches
                    batch_size = 1000
                    total_deleted = 0
                    
                    while True:
                        batch_result = collection.get(limit=batch_size)
                        if not batch_result or not batch_result.get('ids'):
                            break
                        
                        collection.delete(ids=batch_result['ids'])
                        total_deleted += len(batch_result['ids'])
                        print(f"   Deleted {len(batch_result['ids'])} items (total: {total_deleted})")
                        
                        if len(batch_result['ids']) < batch_size:
                            break
                    
                    print(f"✅ Cleared {total_deleted} items from '{collection_name}'")
                else:
                    print(f"✅ Collection '{collection_name}' was already empty")
                
                return True
                
            except Exception as delete_error:
                print(f"❌ Error clearing items from '{collection_name}': {delete_error}")
                # Try to delete the entire collection as fallback
                try:
                    self.chroma_client.delete_collection(collection_name)
                    print(f"✅ Deleted entire collection '{collection_name}' as fallback")
                    return True
                except Exception as collection_delete_error:
                    print(f"❌ Could not delete collection '{collection_name}': {collection_delete_error}")
                    return False
        
        except Exception as e:
            print(f"❌ Error processing collection '{collection_name}': {e}")
            return False

    def clear_all_collections(self) -> bool:
        """Clear all Chroma DB collections"""
        if not self.chroma_client:
            print("❌ Chroma DB not available, skipping collections cleanup")
            return False
        
        try:
            print("🧹 Clearing all Chroma DB collections...")
            
            # Get existing collections
            existing_collections = self.list_collections()
            
            if not existing_collections:
                print("✅ No collections found to clear")
                return True
            
            success = True
            cleared_count = 0
            
            # Clear each collection
            for collection_name in existing_collections:
                if self.clear_collection(collection_name):
                    cleared_count += 1
                else:
                    success = False
            
            print(f"✅ Processed {cleared_count}/{len(existing_collections)} collections successfully")
            return success
            
        except Exception as e:
            print(f"❌ Error clearing Chroma DB collections: {e}")
            return False

    def clear_vector_database_files(self) -> bool:
        """Clear Chroma DB database files completely"""
        if not self.chroma_db_path:
            print("❌ Chroma DB path not found, skipping file cleanup")
            return False
        
        try:
            print(f"🧹 Clearing vector database files at: {self.chroma_db_path}")
            
            if os.path.exists(self.chroma_db_path):
                # Close client connection first
                if self.chroma_client:
                    try:
                        # No explicit close method in chromadb, just reset
                        self.chroma_client = None
                        print("   Closed Chroma DB client connection")
                    except Exception:
                        pass
                
                # List contents before deletion
                try:
                    contents = os.listdir(self.chroma_db_path)
                    print(f"   Found {len(contents)} files/folders to delete: {contents}")
                except Exception as e:
                    print(f"   Could not list directory contents: {e}")
                
                # Remove the entire directory and recreate it
                try:
                    shutil.rmtree(self.chroma_db_path)
                    os.makedirs(self.chroma_db_path, exist_ok=True)
                    print("✅ Cleared vector database files completely")
                    return True
                except Exception as e:
                    print(f"❌ Could not clear vector database files: {e}")
                    print("💡 TIP: Stop the recommendation service first, then try again")
                    return False
            else:
                print(f"✅ Vector database directory doesn't exist: {self.chroma_db_path}")
                return True
                
        except Exception as e:
            print(f"❌ Error clearing vector database files: {e}")
            return False

    def clear_cache_files(self) -> bool:
        """Clear cache files and directories"""
        try:
            print("🧹 Clearing cache files...")
            
            # Cache directories and files to clear
            cache_patterns = [
                '__pycache__',
                '.pytest_cache',
                '.cache',
                'temp',
                'tmp',
                '*.pyc',
                '*.pyo',
                'debug_*',
                'test_cache*',
                'embeddings_cache*'
            ]
            
            cleared_items = []
            
            # Clear cache directories in current directory
            for pattern in cache_patterns:
                if pattern.startswith('*'):
                    # Handle file patterns
                    import glob
                    files = glob.glob(pattern)
                    for file in files:
                        try:
                            if os.path.isfile(file):
                                os.remove(file)
                                cleared_items.append(file)
                                print(f"   Cleared cache file: {file}")
                        except Exception as e:
                            print(f"   Could not clear file {file}: {e}")
                else:
                    # Handle directories
                    if os.path.exists(pattern):
                        try:
                            if os.path.isdir(pattern):
                                shutil.rmtree(pattern)
                                cleared_items.append(pattern)
                                print(f"   Cleared cache directory: {pattern}")
                        except Exception as e:
                            print(f"   Could not clear directory {pattern}: {e}")
            
            # Look for cache directories in subdirectories
            for root, dirs, files in os.walk('.'):
                for cache_dir in ['__pycache__', '.pytest_cache']:
                    if cache_dir in dirs:
                        cache_path = os.path.join(root, cache_dir)
                        try:
                            shutil.rmtree(cache_path)
                            cleared_items.append(cache_path)
                            print(f"   Cleared cache directory: {cache_path}")
                        except Exception as e:
                            print(f"   Could not clear {cache_path}: {e}")
            
            if cleared_items:
                print(f"✅ Cleared {len(cleared_items)} cache items")
            else:
                print("✅ No cache items found to clear")
            
            return True
            
        except Exception as e:
            print(f"❌ Error clearing cache files: {e}")
            return False

    def verify_cleanup(self) -> Dict[str, any]:
        """Verify that cleanup was successful"""
        results = {
            'chroma_collections': 0,
            'chroma_files_exist': False,
            'cache_cleared': False
        }
        
        try:
            # Check Chroma collections
            if self.chroma_client:
                try:
                    collection_names = self.list_collections()
                    total_items = 0
                    for collection_name in collection_names:
                        try:
                            col = self.chroma_client.get_collection(collection_name)
                            result = col.get(limit=1)
                            if result and 'ids' in result:
                                total_items += len(result['ids'])
                        except Exception:
                            pass
                    results['chroma_collections'] = total_items
                except Exception:
                    results['chroma_collections'] = 'Error checking'
            
            # Check if Chroma files exist
            if self.chroma_db_path:
                try:
                    results['chroma_files_exist'] = (
                        os.path.exists(self.chroma_db_path) and 
                        len(os.listdir(self.chroma_db_path)) > 0
                    )
                except Exception:
                    results['chroma_files_exist'] = 'Error checking'
            
            # Check cache directories
            cache_dirs = ['__pycache__', '.pytest_cache', '.cache']
            cache_exists = any(os.path.exists(d) for d in cache_dirs)
            results['cache_cleared'] = not cache_exists
            
        except Exception as e:
            print(f"⚠️  Error during verification: {e}")
        
        return results

    def clear_all_recommendation_data(self) -> bool:
        """Clear all recommendation system data"""
        print("🧹 Starting Recommendation System data cleanup...")
        print("=" * 60)
        
        success = True
        
        # Clear Chroma DB collections
        print("\n🗄️  Clearing Chroma DB collections...")
        if not self.clear_all_collections():
            success = False
        
        # Clear vector database files
        print("\n📁 Clearing vector database files...")
        if not self.clear_vector_database_files():
            success = False
        
        # Clear cache files
        print("\n💾 Clearing cache files...")
        if not self.clear_cache_files():
            success = False
        
        print("\n" + "=" * 60)
        if success:
            print("✅ Recommendation System cleanup completed successfully!")
        else:
            print("⚠️  Recommendation System cleanup completed with some errors")
        
        # Verify cleanup
        print("\n🔍 Verifying cleanup...")
        results = self.verify_cleanup()
        print(f"🗄️  Chroma collections items remaining: {results['chroma_collections']}")
        print(f"📁 Vector database files exist: {results['chroma_files_exist']}")
        print(f"💾 Cache cleared: {results['cache_cleared']}")
        
        return success


def main():
    """Main function to run the recommendation system data cleanup"""
    print("Recommendation System Data Cleanup Script")
    print("=" * 45)
    print("This will clear:")
    print("• All Chroma DB collections (user_events, product_embeddings)")
    print("• Vector database files")
    print("• Cache files and directories")
    print("\n⚠️  WARNING: This action cannot be undone!")
    print("💡 TIP: Stop the recommendation service first for complete cleanup")
    
    # Ask for confirmation
    confirm = input("\nDo you want to continue? (type 'yes' to confirm): ").strip().lower()
    if confirm != 'yes':
        print("❌ Operation cancelled")
        return
    
    # Create cleaner and run cleanup
    cleaner = RecommendationSystemDataCleaner()
    success = cleaner.clear_all_recommendation_data()
    
    if success:
        print("\n🎉 Recommendation System cleanup completed successfully!")
        print("💡 You can now restart the recommendation service with fresh data")
    else:
        print("\n⚠️  Recommendation System cleanup completed with errors.")
        print("💡 If some files couldn't be deleted, stop the recommendation service and try again")


if __name__ == "__main__":
    main()
