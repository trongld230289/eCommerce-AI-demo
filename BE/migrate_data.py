#!/usr/bin/env python3
"""
Data migration script to populate Firebase Fi    "imageUrl": "https://bachlongstore.vn/vnt_upload/product/03_2025/543654890.png",   "imageUrl": "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/c71fde7e-1fdb-4c38-a441-d8ec03deffa8.jpg",estore with product data
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

# Product data with new simplified structure
PRODUCTS_DATA = [
  {
    "name": "Samsung Galaxy S25 Ultra",
    "price": 1299.99,
    "original_price": 1499.99,
    "imageUrl": "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/c71fde7e-1fdb-4c38-a441-d8ec03deffa8.jpg",
    "category": "Phone",
    "description": "Flagship Android phone with 200 MP camera, S Pen support, and advanced AI features.",
    "rating": 4.8,
    "discount": 13
  },
  {
    "name": "Apple iPhone 16 Pro Max",
    "price": 1299.99,
    "original_price": 1499.99,
    "imageUrl": "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/c71fde7e-1fdb-4c38-a441-d8ec03deffa8.jpg",
    "category": "Phone",
    "description": "Premium Apple smartphone with advanced AI, long battery life, and top-tier camera system.",
    "rating": 4.7,
    "discount": 13
  },
  {
    "name": "Nothing Phone 3a Pro",
    "price": 699.99,
    "original_price": 799.99,
    "imageUrl": "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/c71fde7e-1fdb-4c38-a441-d8ec03deffa8.jpg",
    "category": "Phone",
    "description": "Mid-range phone with telephoto and ultrawide cameras and fast 50 W charging.",
    "rating": 4.4,
    "discount": 12
  },
  {
    "name": "Sony Xperia 1 VII",
    "price": 999.99,
    "original_price": 1099.99,
    "imageUrl": "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/c71fde7e-1fdb-4c38-a441-d8ec03deffa8.jpg",
    "category": "Phone",
    "description": "Sony flagship with Snapdragon 8 Elite, 120 Hz OLED display, headphone jack, and expandable storage.",
    "rating": 4.5,
    "discount": 9
  },

  {
    "name": "Asus Zenbook 14 OLED",
    "price": 849.99,
    "original_price": 999.99,
    "imageUrl": "https://bachlongstore.vn/vnt_upload/product/03_2025/543654890.png",
    "category": "Laptop",
    "description": "Well-rounded laptop with 14″ OLED screen, Intel Ultra 5 chip, and 16-hour battery life.",
    "rating": 4.6,
    "discount": 15
  },
  {
    "name": "MacBook Air (M4, 2025)",
    "price": 1199.00,
    "original_price": 1399.99,
    "imageUrl": "https://bachlongstore.vn/vnt_upload/product/03_2025/543654890.png",
    "category": "Laptop",
    "description": "Apple MacBook Air with M4 chip: great balance of performance, battery life, and portability, now in sky blue." ,
    "rating": 4.8,
    "discount": 14
  },
  {
    "name": "MacBook Air (M3, 2024)",
    "price": 999.00,
    "original_price": 1199.99,
    "imageUrl": "https://bachlongstore.vn/vnt_upload/product/03_2025/543654890.png",
    "category": "Laptop",
    "description": "Apple MacBook Air with M3 chip: excellent performance and battery life, perfect for students and professionals.",
    "rating": 4.7,
    "discount": 17
  },
  {
    "name": "MacBook Pro 14-inch (M3)",
    "price": 1199.00,
    "original_price": 1399.99,
    "imageUrl": "https://bachlongstore.vn/vnt_upload/product/03_2025/543654890.png",
    "category": "Laptop",
    "description": "Apple MacBook Pro 14-inch with M3 chip: professional-grade performance with stunning Retina display.",
    "rating": 4.9,
    "discount": 14
  },
  {
    "name": "Lenovo ThinkBook Plus Rollable (Gen 6)",
    "price": 3299.00,
    "original_price": 3499.00,
    "imageUrl": "https://bachlongstore.vn/vnt_upload/product/03_2025/543654890.png",
    "category": "Laptop",
    "description": "First rollable OLED laptop that expands from 14″ to 16.7″; Intel Ultra 7, 32 GB RAM and 1 TB SSD.",
    "rating": 4.3,
    "discount": 6
  },
  {
    "name": "Dell XPS 15 (2025)",
    "price": 1799.99,
    "original_price": 1999.99,
    "imageUrl": "https://bachlongstore.vn/vnt_upload/product/03_2025/543654890.png",
    "category": "Laptop",
    "description": "Premium laptop with InfinityEdge display, strong performance, and elegant design—great for professionals.",
    "rating": 4.7,
    "discount": 10
  },

  {
    "name": "Canon EOS R50 V",
    "price": 699.00,
    "original_price": 849.00,
    "imageUrl": "https://tse1.mm.bing.net/th/id/OIP.NKYikkIRGFkhpPdC7NhIcwHaD4?pid=Api",
    "category": "Camera",
    "description": "Compact mirrorless APS-C camera aimed at vloggers; records 4K/60, has front record button and RF-S mount.",
    "rating": 4.2,
    "discount": 18
  },
  {
    "name": "Fujifilm GFX100RF",
    "price": 4999.99,
    "original_price": 5299.99,
    "imageUrl": "https://tse1.mm.bing.net/th/id/OIP.NKYikkIRGFkhpPdC7NhIcwHaD4?pid=Api",
    "category": "Camera",
    "description": "High-end medium-format camera — one of 2025’s best as per TechRadar.",
    "rating": 4.9,
    "discount": 5
  },
  {
    "name": "Nikon Z5 II",
    "price": 1696.95,
    "original_price": 1896.95,
    "imageUrl": "https://tse1.mm.bing.net/th/id/OIP.NKYikkIRGFkhpPdC7NhIcwHaD4?pid=Api",
    "category": "Camera",
    "description": "Best all-around mirrorless of 2025 — strong stills and video performance at a competitive price.",
    "rating": 4.5,
    "discount": 10
  },
  {
    "name": "Sony a7CR",
    "price": 3198.00,
    "original_price": 3499.00,
    "imageUrl": "https://tse1.mm.bing.net/th/id/OIP.NKYikkIRGFkhpPdC7NhIcwHaD4?pid=Api",
    "category": "Camera",
    "description": "Compact full-frame 61 MP mirrorless with 4K video and AI autofocus — ideal for travel and landscape pursuits.",
    "rating": 4.6,
    "discount": 9
  },
    {
    "name": "Rolex Land-Dweller",
    "price": 800,
    "original_price": 1000,
    "imageUrl": "https://www.swisswatchexpo.com/thewatchclub/wp-content/uploads/2024/12/1Q6A0074.jpg",
    "category": "Watch",
    "description": "Rolex’s first new sport watch in over a decade, featuring a high-frequency caliber and Dynapulse escapement. Available in platinum, rose gold, and white Rolesor in 36 mm and 40 mm sizes.",
    "rating": 4.9,
    "discount": 20
  },
  {
    "name": "Vacheron Constantin Les Cabinotiers Solaria Ultra Grand Complication",
    "price": 1600,
    "original_price": 2000,
    "imageUrl": "https://www.swisswatchexpo.com/thewatchclub/wp-content/uploads/2024/12/1Q6A0074.jpg",
    "category": "Watch",
    "description": "Arguably the most complicated wristwatch ever, with 1,521 components and 41 complications including stellar positions and solar trajectories.",
    "rating": 5.0,
    "discount": 20
  },
  {
    "name": "Bianchet B 1.618 UltraFino Carbon",
    "price": 1800,
    "original_price": 2000,
    "imageUrl": "https://www.swisswatchexpo.com/thewatchclub/wp-content/uploads/2024/12/1Q6A0074.jpg",
    "category": "Watch",
    "description": "Tonneau-shaped ultra-thin sport watch with integrated carbon bracelet and first automatic flying tourbillon in titanium (caliber UT01).",
    "rating": 4.8,
    "discount": 10
  },
  {
    "name": "NORQAIN Freedom 60 Chrono 'Enjoy Life' Special Edition",
    "price": 2700,
    "original_price": 3000,
    "imageUrl": "https://www.swisswatchexpo.com/thewatchclub/wp-content/uploads/2024/12/1Q6A0074.jpg",
    "category": "Watch",
    "description": "Swiss-made chronograph with retro-inspired design and playful summer details like an ice cream cone motif—endorsed by Mark Wahlberg as the “watch of the summer.”",
    "rating": 4.6,
    "discount": 10
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
                # Prepare product document with only the required fields
                product_dict = product_data.copy()
                product_dict['id'] = i
                product_dict['created_at'] = time.time()
                product_dict['updated_at'] = time.time()
                
                # Ensure required fields have defaults for new simplified model
                if 'rating' not in product_dict:
                    product_dict['rating'] = 4.0
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
        
        # Get categories
        categories = set()
        
        for product in PRODUCTS_DATA:
            if product.get('category'):
                categories.add(product['category'])
        
        print(f"   • Categories: {len(categories)} ({', '.join(sorted(categories))})")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise e

if __name__ == "__main__":
    migrate_products()
