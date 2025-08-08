#!/usr/bin/env python3
"""
Clear Backend Data Script
=========================
This script clears data from:
1. Firebase Firestore (products and events)
2. Cache files

Use with caution - this will delete all backend data!
Note: Chroma DB/Vector data is handled by AI_Service/Recommendation_System
"""

import os
import sys
import shutil
from typing import Optional
from dotenv import load_dotenv

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import Firebase configuration
try:
    from firebase_config import FirebaseConfig
    FIREBASE_AVAILABLE = True
except ImportError:
    print("⚠️  Firebase configuration not available")
    FIREBASE_AVAILABLE = False

class BackendDataCleaner:
    """Comprehensive data cleaner for Firebase and Cache only"""
    
    def __init__(self):
        self.firebase_config = None
        
        # Initialize Firebase
        if FIREBASE_AVAILABLE:
            try:
                self.firebase_config = FirebaseConfig()
                print("✅ Firebase initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize Firebase: {e}")
                self.firebase_config = None

    def clear_firebase_products(self) -> bool:
        """Clear all products from Firebase Firestore"""
        if not self.firebase_config or not self.firebase_config.db:
            print("❌ Firebase not available, skipping products cleanup")
            return False
        
        try:
            print("🧹 Clearing Firebase products...")
            products_ref = self.firebase_config.db.collection('products')
            
            # Get all products
            products = products_ref.stream()
            count = 0
            
            # Delete products in batches
            batch = self.firebase_config.db.batch()
            batch_count = 0
            
            for product in products:
                batch.delete(product.reference)
                batch_count += 1
                count += 1
                
                # Commit batch every 500 items (Firestore limit)
                if batch_count >= 500:
                    batch.commit()
                    batch = self.firebase_config.db.batch()
                    batch_count = 0
                    print(f"   Deleted {count} products so far...")
            
            # Commit remaining items
            if batch_count > 0:
                batch.commit()
            
            print(f"✅ Cleared {count} products from Firebase")
            return True
            
        except Exception as e:
            print(f"❌ Error clearing Firebase products: {e}")
            return False

    def clear_firebase_events(self) -> bool:
        """Clear all events from Firebase Firestore"""
        if not self.firebase_config or not self.firebase_config.db:
            print("❌ Firebase not available, skipping events cleanup")
            return False
        
        try:
            print("🧹 Clearing Firebase events...")
            
            # Clear different types of events
            event_collections = [
                'events'
            ]
            
            total_count = 0
            
            for collection_name in event_collections:
                try:
                    events_ref = self.firebase_config.db.collection(collection_name)
                    events = events_ref.stream()
                    count = 0
                    
                    # Delete events in batches
                    batch = self.firebase_config.db.batch()
                    batch_count = 0
                    
                    for event in events:
                        batch.delete(event.reference)
                        batch_count += 1
                        count += 1
                        
                        # Commit batch every 500 items
                        if batch_count >= 500:
                            batch.commit()
                            batch = self.firebase_config.db.batch()
                            batch_count = 0
                    
                    # Commit remaining items
                    if batch_count > 0:
                        batch.commit()
                    
                    if count > 0:
                        print(f"   Cleared {count} events from '{collection_name}' collection")
                        total_count += count
                        
                except Exception:
                    # Collection might not exist, that's okay
                    pass
            
            print(f"✅ Cleared {total_count} total events from Firebase")
            return True
            
        except Exception as e:
            print(f"❌ Error clearing Firebase events: {e}")
            return False

    def clear_cache_files(self) -> bool:
        """Clear cache files and directories"""
        try:
            print("🧹 Clearing cache files...")
            
            # Common cache directories to check and clear
            cache_dirs = [
                '__pycache__',
                '.pytest_cache', 
                '.cache',
                'temp',
                'tmp'
            ]
            
            cleared_dirs = []
            
            # Clear cache directories in current directory
            for cache_dir in cache_dirs:
                if os.path.exists(cache_dir):
                    try:
                        shutil.rmtree(cache_dir)
                        cleared_dirs.append(cache_dir)
                        print(f"   Cleared cache directory: {cache_dir}")
                    except Exception as e:
                        print(f"   Could not clear {cache_dir}: {e}")
            
            if cleared_dirs:
                print(f"✅ Cleared {len(cleared_dirs)} cache directories")
            else:
                print("✅ No cache directories found to clear")
            
            return True
            
        except Exception as e:
            print(f"❌ Error clearing cache files: {e}")
            return False

    def verify_cleanup(self) -> dict:
        """Verify that backend data has been cleared"""
        verification = {
            'firebase_products': 0,
            'firebase_events': 0,
            'cache_cleared': False
        }
        
        try:
            # Check Firebase products
            if self.firebase_config and self.firebase_config.db:
                try:
                    products = list(self.firebase_config.db.collection('products').limit(1).stream())
                    verification['firebase_products'] = len(products)
                except Exception:
                    pass
                
                # Check Firebase events
                try:
                    events = list(self.firebase_config.db.collection('events').limit(1).stream())
                    verification['firebase_events'] = len(events)
                except Exception:
                    pass
            
            # Check cache directories
            cache_dirs = ['__pycache__', '.pytest_cache', '.cache']
            cache_exists = any(os.path.exists(d) for d in cache_dirs)
            verification['cache_cleared'] = not cache_exists
            
        except Exception as e:
            print(f"⚠️  Error during verification: {e}")
        
        return verification

    def clear_all_backend_data(self) -> bool:
        """Clear all backend data (Firebase + cache)"""
        print("🧹 Starting backend data cleanup...")
        print("=" * 50)
        
        success = True
        
        # Clear Firebase data
        print("\n📊 Clearing Firebase data...")
        if not self.clear_firebase_products():
            success = False
        if not self.clear_firebase_events():
            success = False
        
        # Clear cache files
        print("\n💾 Clearing cache files...")
        if not self.clear_cache_files():
            success = False
        
        print("\n" + "=" * 50)
        if success:
            print("✅ Backend data cleanup completed successfully!")
        else:
            print("⚠️  Backend data cleanup completed with some errors")
        
        # Verify cleanup
        print("\n� Verifying cleanup...")
        results = self.verify_cleanup()
        print(f"📊 Firebase products remaining: {results['firebase_products']}")
        print(f"📊 Firebase events remaining: {results['firebase_events']}")
        print(f"💾 Cache cleared: {results['cache_cleared']}")
        
        return success


def main():
    """Main function to run the backend data cleanup"""
    print("Backend Data Cleanup Script")
    print("=" * 30)
    print("This will clear:")
    print("• All products from Firebase Firestore")
    print("• All events from Firebase Firestore")
    print("• Cache files and directories")
    print("\n⚠️  WARNING: This action cannot be undone!")
    
    # Ask for confirmation
    confirm = input("\nDo you want to continue? (type 'yes' to confirm): ").strip().lower()
    if confirm != 'yes':
        print("❌ Operation cancelled")
        return
    
    # Create cleaner and run cleanup
    cleaner = BackendDataCleaner()
    success = cleaner.clear_all_backend_data()
    
    if success:
        print("\n🎉 Backend cleanup completed successfully!")
    else:
        print("\n⚠️  Backend cleanup completed with errors. Check the output above.")


if __name__ == "__main__":
    main()
