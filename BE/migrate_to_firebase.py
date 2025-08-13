#!/usr/bin/env python3
"""
Firebase Data Migration Script
Migrates mock product data to Firebase Firestore for the FastAPI backend

NOTE: This migration has been completed successfully.
This file is kept for reference and can be removed if no longer needed.
Data has already been migrated to Firebase Firestore.
"""

import sys
import os
from datetime import datetime, timezone
from firebase_config import get_firestore_db

# Mock data for FastAPI backend
MOCK_PRODUCTS = [
    {
        "id": 1,
        "name": "Wireless Bluetooth Headphones",
        "description": "High-quality wireless headphones with noise cancellation",
        "price": 99.99,
        "category": "Electronics",
        "brand": "AudioTech",
        "imageUrl": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
        "stock": 50,
        "rating": 4.5,
        "featured": True,
        "weeklyViews": 1250,
        "weeklySales": 45
    },
    {
        "id": 2,
        "name": "Smart Fitness Watch",
        "description": "Track your fitness goals with this advanced smartwatch",
        "price": 299.99,
        "category": "Electronics",
        "brand": "FitTech",
        "imageUrl": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500",
        "stock": 30,
        "rating": 4.7,
        "featured": True,
        "weeklyViews": 980,
        "weeklySales": 32
    },
    {
        "id": 3,
        "name": "Portable Laptop Stand",
        "description": "Ergonomic adjustable laptop stand for better posture",
        "price": 49.99,
        "category": "Accessories",
        "brand": "ErgoDesk",
        "imageUrl": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500",
        "stock": 75,
        "rating": 4.3,
        "featured": False,
        "weeklyViews": 650,
        "weeklySales": 28
    },
    {
        "id": 4,
        "name": "USB-C Hub",
        "description": "Multi-port USB-C hub with HDMI, USB-A, and SD card slots",
        "price": 79.99,
        "category": "Accessories",
        "brand": "TechConnect",
        "imageUrl": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=500",
        "stock": 40,
        "rating": 4.4,
        "featured": True,
        "weeklyViews": 820,
        "weeklySales": 38
    },
    {
        "id": 5,
        "name": "Wireless Charging Pad",
        "description": "Fast wireless charging pad compatible with all Qi devices",
        "price": 34.99,
        "category": "Accessories",
        "brand": "PowerWave",
        "imageUrl": "https://images.unsplash.com/photo-1609592067784-e4a9d8f1b3d1?w=500",
        "stock": 60,
        "rating": 4.2,
        "featured": False,
        "weeklyViews": 450,
        "weeklySales": 22
    },
    {
        "id": 6,
        "name": "Gaming Mechanical Keyboard",
        "description": "RGB backlit mechanical keyboard for gaming enthusiasts",
        "price": 149.99,
        "category": "Gaming",
        "brand": "GameForce",
        "imageUrl": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=500",
        "stock": 25,
        "rating": 4.8,
        "featured": True,
        "weeklyViews": 1100,
        "weeklySales": 42
    },
    {
        "id": 7,
        "name": "Noise-Cancelling Earbuds",
        "description": "Premium wireless earbuds with active noise cancellation",
        "price": 199.99,
        "category": "Electronics",
        "brand": "AudioTech",
        "imageUrl": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500",
        "stock": 35,
        "rating": 4.6,
        "featured": True,
        "weeklyViews": 1350,
        "weeklySales": 48
    },
    {
        "id": 8,
        "name": "Smart Home Security Camera",
        "description": "1080p HD security camera with night vision and mobile alerts",
        "price": 129.99,
        "category": "Smart Home",
        "brand": "SecureVision",
        "imageUrl": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500",
        "stock": 42,
        "rating": 4.4,
        "featured": False,
        "weeklyViews": 890,
        "weeklySales": 35
    }
]

def migrate_products_to_firestore():
    """Migrate mock products to Firestore"""
    try:
        print("🚀 Starting Firebase migration...")
        
        # Get Firestore database
        db = get_firestore_db()
        if db is None:
            print("❌ Failed to connect to Firestore. Please check your Firebase configuration.")
            return False
        
        # Reference to products collection
        products_ref = db.collection('products')
        
        # Check if products already exist
        existing_products = products_ref.limit(1).get()
        if len(existing_products) > 0:
            response = input("⚠️  Products collection already exists. Do you want to overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Migration cancelled.")
                return False
        
        # Add timestamp for tracking
        current_time = datetime.now(timezone.utc)
        
        print(f"📦 Migrating {len(MOCK_PRODUCTS)} products to Firestore...")
        
        # Batch write for better performance
        batch = db.batch()
        
        for product in MOCK_PRODUCTS:
            # Add metadata
            product_data = product.copy()
            product_data['createdAt'] = current_time
            product_data['updatedAt'] = current_time
            product_data['migrated'] = True
            
            # Use product ID as document ID
            doc_ref = products_ref.document(str(product['id']))
            batch.set(doc_ref, product_data)
            
            print(f"  ✅ Prepared: {product['name']}")
        
        # Commit the batch
        batch.commit()
        
        print("\n🎉 Migration completed successfully!")
        print(f"📊 Migrated {len(MOCK_PRODUCTS)} products to Firebase Firestore")
        print("🔗 Collection: 'products'")
        print("📍 Project: ecommerce-ai-cfafd")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def verify_migration():
    """Verify that products were migrated successfully"""
    try:
        print("\n🔍 Verifying migration...")
        
        db = get_firestore_db()
        if db is None:
            print("❌ Cannot verify - no database connection")
            return False
        
        # Get all products
        products_ref = db.collection('products')
        products = products_ref.get()
        
        print(f"✅ Found {len(products)} products in Firestore")
        
        # Show sample data
        for i, doc in enumerate(products[:3]):
            product = doc.to_dict()
            print(f"  📦 {product.get('name', 'Unknown')} - ${product.get('price', 0)}")
            if i == 2 and len(products) > 3:
                print(f"  ... and {len(products) - 3} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    """Main migration function"""
    print("🔥 Firebase Product Data Migration Tool")
    print("=" * 50)
    
    # Run migration
    success = migrate_products_to_firestore()
    
    if success:
        # Verify migration
        verify_migration()
        print("\n✨ Next steps:")
        print("1. Update your Flask server to use Firestore data")
        print("2. Test your APIs with real Firebase data")
        print("3. Consider adding data validation and error handling")
    else:
        print("\n❌ Migration failed. Please check your Firebase configuration.")
        print("Make sure:")
        print("- serviceAccountKey.json is in the BE folder")
        print("- Firebase project 'ecommerce-ai-cfafd' exists")
        print("- Firestore database is enabled")

if __name__ == "__main__":
    main()
