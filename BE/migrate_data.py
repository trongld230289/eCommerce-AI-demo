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
from firebase_config import get_firestore_db
from models import ProductCreate

# Product data extracted from frontend (mockData.ts and Products.tsx)
PRODUCTS_DATA = [
    # Products from mockData.ts
    {
        "name": "iPhone 15 Pro",
        "price": 999.99,
        "original_price": 1099.99,
        "image": "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=400",
        "category": "Điện thoại",
        "description": "Latest iPhone with A17 Pro chip",
        "brand": "Apple",
        "tags": ["smartphone", "apple", "ios"],
        "rating": 4.8,
        "is_new": True,
        "discount": 100
    },
    {
        "name": "Samsung Galaxy S24 Ultra",
        "price": 899.99,
        "original_price": 999.99,
        "image": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400",
        "category": "Điện thoại",
        "description": "Smartphone Android flagship với S Pen",
        "brand": "Samsung",
        "rating": 4.7
    },
    {
        "name": "Dell XPS 13",
        "price": 18000000,
        "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400",
        "category": "Laptop",
        "description": "Laptop siêu mỏng với màn hình 13.3 inch",
        "brand": "Dell",
        "rating": 4.6
    },
    {
        "name": "MacBook Air M3",
        "price": 24000000,
        "image": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400",
        "category": "Laptop",
        "description": "Laptop Apple với chip M3 hiệu năng cao",
        "brand": "Apple",
        "rating": 4.9
    },
    {
        "name": "Sony WH-1000XM5",
        "price": 8500000,
        "image": "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400",
        "category": "Tai nghe",
        "description": "Tai nghe chống ồn cao cấp",
        "brand": "Sony",
        "rating": 4.8
    },
    {
        "name": "iPad Pro 12.9\"",
        "price": 20000000,
        "image": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400",
        "category": "Máy tính bảng",
        "description": "Máy tính bảng chuyên nghiệp với chip M2",
        "brand": "Apple",
        "rating": 4.7
    },
    {
        "name": "Samsung Galaxy Watch 6",
        "price": 6500000,
        "image": "https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?w=400",
        "category": "Đồng hồ thông minh",
        "description": "Đồng hồ thông minh với tính năng sức khỏe",
        "brand": "Samsung",
        "rating": 4.5
    },
    {
        "name": "Canon EOS R6 Mark II",
        "price": 45000000,
        "image": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=400",
        "category": "Máy ảnh",
        "description": "Máy ảnh mirrorless chuyên nghiệp",
        "brand": "Canon",
        "rating": 4.9
    },
    {
        "name": "Nintendo Switch OLED",
        "price": 8000000,
        "image": "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=400",
        "category": "Máy chơi game",
        "description": "Máy chơi game cầm tay với màn hình OLED",
        "brand": "Nintendo",
        "rating": 4.6
    },
    {
        "name": "LG OLED C3 55\"",
        "price": 35000000,
        "image": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400",
        "category": "TV",
        "description": "Smart TV OLED 4K với AI ThinQ",
        "brand": "LG",
        "rating": 4.8
    },
    # Additional products from Products.tsx
    {
        "name": "Wireless Headphones",
        "price": 99.99,
        "original_price": 129.99,
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
        "category": "Electronics",
        "description": "High-quality wireless headphones with noise cancellation",
        "brand": "AudioTech",
        "tags": ["wireless", "bluetooth", "noise-cancellation", "music"],
        "color": "Black",
        "rating": 4.5,
        "is_new": True,
        "discount": 30
    },
    {
        "name": "Smart Watch",
        "price": 299.99,
        "original_price": 349.99,
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500",
        "category": "Electronics",
        "description": "Advanced smartwatch with health monitoring and GPS",
        "brand": "TechWatch",
        "tags": ["smartwatch", "fitness", "health", "gps", "waterproof"],
        "color": "Silver",
        "rating": 4.7,
        "discount": 50
    },
    {
        "name": "Gaming Laptop",
        "price": 999.99,
        "original_price": 1199.99,
        "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500",
        "category": "Electronics",
        "description": "High-performance laptop for work and gaming with RTX graphics",
        "brand": "GameMaster",
        "tags": ["laptop", "gaming", "rtx", "high-performance", "work"],
        "color": "Black",
        "rating": 4.8,
        "discount": 200
    },
    {
        "name": "Smartphone Pro",
        "price": 699.99,
        "original_price": 799.99,
        "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500",
        "category": "Electronics",
        "description": "Latest smartphone with amazing camera and 5G connectivity",
        "brand": "PhoneTech",
        "tags": ["smartphone", "camera", "5g", "photography", "mobile"],
        "color": "Blue",
        "rating": 4.6,
        "discount": 100
    },
    {
        "name": "Portable Bluetooth Speaker",
        "price": 79.99,
        "original_price": 99.99,
        "image": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=500",
        "category": "Electronics",
        "description": "Portable bluetooth speaker with great sound and long battery life",
        "brand": "SoundWave",
        "tags": ["speaker", "bluetooth", "portable", "bass", "waterproof"],
        "color": "Red",
        "rating": 4.3,
        "discount": 20
    },
    {
        "name": "RGB Gaming Mouse",
        "price": 49.99,
        "original_price": 69.99,
        "image": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500",
        "category": "Electronics",
        "description": "Professional gaming mouse with RGB lighting and precision sensor",
        "brand": "GamerGear",
        "tags": ["mouse", "gaming", "rgb", "precision", "esports"],
        "color": "Black",
        "rating": 4.4,
        "discount": 20
    },
    {
        "name": "Mechanical Gaming Keyboard",
        "price": 129.99,
        "original_price": 159.99,
        "image": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=500",
        "category": "Electronics",
        "description": "Mechanical keyboard for gaming and typing with RGB backlight",
        "brand": "KeyMaster",
        "tags": ["keyboard", "mechanical", "gaming", "rgb", "typing"],
        "color": "Black",
        "rating": 4.7,
        "discount": 30
    },
    {
        "name": "iPad Tablet",
        "price": 399.99,
        "original_price": 449.99,
        "image": "https://images.unsplash.com/photo-1561154464-82e9adf32764?w=500",
        "category": "Electronics",
        "description": "Lightweight tablet for work and entertainment with stylus support",
        "brand": "TabletPro",
        "tags": ["tablet", "stylus", "drawing", "work", "entertainment"],
        "color": "White",
        "rating": 4.5,
        "discount": 50
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
                if 'is_new' not in product_dict:
                    product_dict['is_new'] = False
                if 'discount' not in product_dict:
                    product_dict['discount'] = 0
                
                # Add to Firestore
                doc_ref = db.collection(collection_name).document(str(i))
                doc_ref.set(product_dict)
                
                print(f"✓ Migrated product {i}: {product_dict['name']}")
                
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
