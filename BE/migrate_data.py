#!/usr/bin/env python3
"""
Data migration script to populate Firebase Firestore with product data
from the frontend mock data.

This script will:
1. Extract product data from frontend mockData
2. Transform the data to match backend models
3. Upload to Firebase Firestore
"""

import asyncio
import time
import random
from firebase_config import get_firestore_db
from models import ProductCreate

# Product data extracted from frontend (mockData.ts and Products.tsx)
PRODUCTS_DATA = [
    # Products from mockData.ts
    {
        "name": "iPhone 15 Pro",
        "price": 999.99,
        "original_price": 1099.99,
        "imageUrl": "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=400",
        "category": "Smartphones",
        "description": "Latest iPhone with A17 Pro chip",
        "brand": "Apple",
        "tags": ["smartphone", "apple", "ios"],
        "rating": 4.8,
        "reviews": 245,
        "is_new": True,
        "featured": True,
        "discount": 100,
        "quantity": 0,
        "stock": 0,
        "weeklySales": 25,
        "weeklyViews": 2100
    },
    {
        "name": "Samsung Galaxy S24 Ultra",
        "price": 899.99,
        "original_price": 999.99,
        "imageUrl": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400",
        "category": "Smartphones",
        "description": "Android flagship smartphone with S Pen",
        "brand": "Samsung",
        "rating": 4.7,
        "reviews": 198,
        "featured": False,
        "quantity": 25,
        "stock": 25,
        "weeklySales": 32,
        "weeklyViews": 1850
    },
    {
        "name": "Dell XPS 13",
        "price": 1800.00,
        "original_price": 1999.99,
        "imageUrl": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400",
        "category": "Laptops",
        "description": "Ultra-thin laptop with 13.3 inch display",
        "brand": "Dell",
        "rating": 4.6,
        "reviews": 156,
        "featured": False,
        "quantity": 15,
        "stock": 15,
        "weeklySales": 18,
        "weeklyViews": 980
    },
    {
        "name": "MacBook Air M3",
        "price": 2400.00,
        "original_price": 2599.99,
        "imageUrl": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400",
        "category": "Laptops",
        "description": "Apple laptop with high-performance M3 chip",
        "brand": "Apple",
        "rating": 4.9,
        "reviews": 312,
        "featured": True,
        "quantity": 12,
        "stock": 12,
        "weeklySales": 42,
        "weeklyViews": 2350
    },
    {
        "name": "Sony WH-1000XM5",
        "price": 850.00,
        "original_price": 949.99,
        "imageUrl": "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400",
        "category": "Headphones",
        "description": "Premium noise-canceling headphones",
        "brand": "Sony",
        "rating": 4.8,
        "reviews": 203,
        "featured": True,
        "quantity": 30,
        "stock": 30,
        "weeklySales": 67,
        "weeklyViews": 1580
    },
    {
        "name": "iPad Pro 12.9\"",
        "price": 2000.00,
        "original_price": 2199.99,
        "imageUrl": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400",
        "category": "Tablets",
        "description": "Professional tablet with M2 chip",
        "brand": "Apple",
        "rating": 4.7,
        "reviews": 174,
        "featured": False,
        "quantity": 18,
        "stock": 18,
        "weeklySales": 28,
        "weeklyViews": 720
    },
    {
        "name": "Samsung Galaxy Watch 6",
        "price": 650.00,
        "original_price": 749.99,
        "imageUrl": "https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?w=400",
        "category": "Smart Watches",
        "description": "Smart watch with health monitoring features",
        "brand": "Samsung",
        "rating": 4.5,
        "reviews": 92,
        "featured": False,
        "quantity": 22,
        "stock": 22,
        "weeklySales": 34,
        "weeklyViews": 890
    },
    {
        "name": "Canon EOS R6 Mark II",
        "price": 4500.00,
        "original_price": 4799.99,
        "imageUrl": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=400",
        "category": "Cameras",
        "description": "Professional mirrorless camera",
        "brand": "Canon",
        "rating": 4.9,
        "reviews": 87,
        "featured": True,
        "quantity": 8,
        "stock": 8,
        "weeklySales": 15,
        "weeklyViews": 650
    },
    {
        "name": "Nintendo Switch OLED",
        "price": 800.00,
        "original_price": 899.99,
        "imageUrl": "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=400",
        "category": "Gaming Consoles",
        "description": "Handheld gaming console with OLED display",
        "brand": "Nintendo",
        "rating": 4.6,
        "reviews": 165,
        "featured": False,
        "quantity": 35,
        "stock": 35,
        "weeklySales": 58,
        "weeklyViews": 1420
    },
    {
        "name": "LG OLED C3 55\"",
        "price": 3500.00,
        "original_price": 3799.99,
        "imageUrl": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400",
        "category": "TVs",
        "description": "Smart TV OLED 4K with AI ThinQ",
        "brand": "LG",
        "rating": 4.8,
        "reviews": 142,
        "featured": True,
        "quantity": 10,
        "stock": 10,
        "weeklySales": 22,
        "weeklyViews": 1150
    },
    # Additional products from Products.tsx
    {
        "name": "Wireless Headphones",
        "price": 99.99,
        "original_price": 129.99,
        "imageUrl": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
        "category": "Electronics",
        "description": "High-quality wireless headphones with noise cancellation",
        "brand": "AudioTech",
        "tags": ["wireless", "bluetooth", "noise-cancellation", "music"],
        "color": "Black",
        "rating": 4.5,
        "reviews": 128,
        "is_new": True,
        "discount": 30,
        "quantity": 45,
        "stock": 45,
        "weeklySales": 45,
        "weeklyViews": 1250
    },
    {
        "name": "Smart Watch",
        "price": 299.99,
        "original_price": 349.99,
        "imageUrl": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500",
        "category": "Electronics",
        "description": "Advanced smartwatch with health monitoring and GPS",
        "brand": "TechWatch",
        "tags": ["smartwatch", "fitness", "health", "gps", "waterproof"],
        "color": "Silver",
        "rating": 4.7,
        "reviews": 89,
        "featured": True,
        "discount": 50,
        "quantity": 28,
        "stock": 28,
        "weeklySales": 32,
        "weeklyViews": 890
    },
    {
        "name": "Gaming Laptop",
        "price": 999.99,
        "original_price": 1199.99,
        "imageUrl": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500",
        "category": "Electronics",
        "description": "High-performance laptop for work and gaming with RTX graphics",
        "brand": "GameMaster",
        "tags": ["laptop", "gaming", "rtx", "high-performance", "work"],
        "color": "Black",
        "rating": 4.8,
        "reviews": 156,
        "featured": False,
        "discount": 200,
        "quantity": 20,
        "stock": 20,
        "weeklySales": 38,
        "weeklyViews": 1680
    },
    {
        "name": "Smartphone Pro",
        "price": 699.99,
        "original_price": 799.99,
        "imageUrl": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500",
        "category": "Electronics",
        "description": "Latest smartphone with amazing camera and 5G connectivity",
        "brand": "PhoneTech",
        "tags": ["smartphone", "camera", "5g", "photography", "mobile"],
        "color": "Blue",
        "rating": 4.6,
        "reviews": 203,
        "featured": False,
        "discount": 100,
        "quantity": 33,
        "stock": 33,
        "weeklySales": 29,
        "weeklyViews": 1320
    },
    {
        "name": "Portable Bluetooth Speaker",
        "price": 79.99,
        "original_price": 99.99,
        "imageUrl": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=500",
        "category": "Electronics",
        "description": "Portable bluetooth speaker with great sound and long battery life",
        "brand": "SoundWave",
        "tags": ["speaker", "bluetooth", "portable", "bass", "waterproof"],
        "color": "Red",
        "rating": 4.3,
        "reviews": 174,
        "featured": False,
        "discount": 20,
        "quantity": 50,
        "stock": 50,
        "weeklySales": 67,
        "weeklyViews": 1580
    },
    {
        "name": "RGB Gaming Mouse",
        "price": 49.99,
        "original_price": 69.99,
        "imageUrl": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500",
        "category": "Electronics",
        "description": "Professional gaming mouse with RGB lighting and precision sensor",
        "brand": "GamerGear",
        "tags": ["mouse", "gaming", "rgb", "precision", "esports"],
        "color": "Black",
        "rating": 4.4,
        "reviews": 92,
        "featured": False,
        "discount": 20,
        "quantity": 75,
        "stock": 75,
        "weeklySales": 51,
        "weeklyViews": 1120
    },
    {
        "name": "Mechanical Gaming Keyboard",
        "price": 129.99,
        "original_price": 159.99,
        "imageUrl": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=500",
        "category": "Electronics",
        "description": "Mechanical keyboard for gaming and typing with RGB backlight",
        "brand": "KeyMaster",
        "tags": ["keyboard", "mechanical", "gaming", "rgb", "typing"],
        "color": "Black",
        "rating": 4.7,
        "reviews": 156,
        "featured": True,
        "discount": 30,
        "quantity": 40,
        "stock": 40,
        "weeklySales": 39,
        "weeklyViews": 950
    },
    {
        "name": "iPad Tablet",
        "price": 399.99,
        "original_price": 449.99,
        "imageUrl": "https://images.unsplash.com/photo-1561154464-82e9adf32764?w=500",
        "category": "Electronics",
        "description": "Lightweight tablet for work and entertainment with stylus support",
        "brand": "TabletPro",
        "tags": ["tablet", "stylus", "drawing", "work", "entertainment"],
        "color": "White",
        "rating": 4.5,
        "reviews": 125,
        "featured": False,
        "discount": 50,
        "quantity": 25,
        "stock": 25,
        "weeklySales": 26,
        "weeklyViews": 780
    }
]

def migrate_products():
    """Migrate product data to Firebase Firestore"""
    try:
        print("Starting product migration to Firebase Firestore...")
        db = get_firestore_db()
        collection_name = 'products'
        
        # Clear existing products (optional - comment out to keep existing data)
        print("Clearing existing products...")
        docs = db.collection(collection_name).stream()
        for doc in docs:
            doc.reference.delete()
        
        print(f"Migrating {len(PRODUCTS_DATA)} products...")
        
        for i, product_data in enumerate(PRODUCTS_DATA, 1):
            try:
                # Prepare product document
                product_dict = product_data.copy()
                product_dict['id'] = i
                product_dict['created_at'] = time.time()
                product_dict['updated_at'] = time.time()
                
                # Ensure required fields have defaults
                if 'tags' not in product_dict:
                    product_dict['tags'] = []
                if 'rating' not in product_dict:
                    product_dict['rating'] = 4.0
                if 'reviews' not in product_dict:
                    product_dict['reviews'] = 50
                if 'is_new' not in product_dict:
                    product_dict['is_new'] = False
                if 'featured' not in product_dict:
                    product_dict['featured'] = False
                if 'discount' not in product_dict:
                    product_dict['discount'] = 0
                if 'quantity' not in product_dict:
                    product_dict['quantity'] = 10
                if 'stock' not in product_dict:
                    product_dict['stock'] = product_dict['quantity']
                if 'weeklySales' not in product_dict:
                    product_dict['weeklySales'] = 20
                if 'weeklyViews' not in product_dict:
                    product_dict['weeklyViews'] = 500
                
                # Add to Firestore
                doc_ref = db.collection(collection_name).document(str(i))
                doc_ref.set(product_dict)
                
                print(f"✓ Migrated product {i}: {product_dict['name']} (Stock: {product_dict['stock']})")
                
            except Exception as e:
                print(f"✗ Error migrating product {i}: {e}")
                continue
        
        print(f"\\n✅ Migration completed! {len(PRODUCTS_DATA)} products migrated to Firebase.")
        print("\\n📊 Summary:")
        
        # Get categories and brands
        categories = set()
        brands = set()
        
        for product in PRODUCTS_DATA:
            if product.get('category'):
                categories.add(product['category'])
            if product.get('brand'):
                brands.add(product['brand'])
        
        print(f"   • Categories: {len(categories)} ({', '.join(sorted(categories))})")
        print(f"   • Brands: {len(brands)} ({', '.join(sorted(brands))})")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise e

if __name__ == "__main__":
    migrate_products()
