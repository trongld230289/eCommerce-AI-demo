#!/usr/bin/env python3
"""
Data migration script v2 with embedding generation and ChromaDB integration
"""

import asyncio
import time
import random
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
import openai
import chromadb
from chromadb.config import Settings
from firebase_config import get_firestore_db
from models import ProductCreate, Product
from product_service import ProductService
from utils.product_keywords import get_product_keywords_from_dict

# Load environment variables
load_dotenv()

# Updated product data with more reliable and product-appropriate image URLs
PRODUCTS_DATA = [
    # PHONE CATEGORY (Samsung, iPhone, Xiaomi)
    {
        "name": "Samsung Galaxy S24 Ultra",
        "price": 1299.99,
        "original_price": 1499.99,
        "imageUrl": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=500&h=500&fit=crop&crop=center",
        "category": "Phone",
        "description": "Flagship Samsung phone with 200MP camera, S Pen support, and AI features.",
        "rating": 4.8,
        "discount": 13
    },
    {
        "name": "Samsung Galaxy S24",
        "price": 899.99,
        "original_price": 999.99,
        "imageUrl": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&h=500&fit=crop&crop=center",
        "category": "Phone",
        "description": "Compact Samsung flagship with advanced camera and premium build quality.",
        "rating": 4.7,
        "discount": 10
    },
    {
        "name": "Samsung Galaxy A55",
        "price": 449.99,
        "original_price": 499.99,
        "imageUrl": "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=500&h=500&fit=crop&crop=center",
        "category": "Phone",
        "description": "Mid-range Samsung phone with excellent camera and long battery life.",
        "rating": 4.4,
        "discount": 10
    },
    {
        "name": "iPhone 15 Pro Max",
        "price": 1199.99,
        "original_price": 1299.99,
        "imageUrl": "https://images.unsplash.com/photo-1574944985070-8f3ebc6b79d2?w=500&h=500&fit=crop&crop=center",
        "category": "Phone",
        "description": "Premium iPhone with titanium design, advanced cameras, and A17 Pro chip.",
        "rating": 4.8,
        "discount": 8
    },
    {
        "name": "iPhone 15",
        "price": 799.99,
        "original_price": 899.99,
        "imageUrl": "https://images.unsplash.com/photo-1556656793-08538906a9f8?w=500&h=500&fit=crop&crop=center",
        "category": "Phone",
        "description": "Latest iPhone with Dynamic Island, advanced camera system, and USB-C.",
        "rating": 4.6,
        "discount": 11
    },
    {
        "name": "iPhone 14",
        "price": 599.99,
        "original_price": 699.99,
        "imageUrl": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=500&h=500&fit=crop&crop=center",
        "category": "Phone",
        "description": "Reliable iPhone with excellent camera performance and iOS experience.",
        "rating": 4.5,
        "discount": 14
    },
    {
        "name": "Xiaomi 14 Ultra",
        "price": 1199.99,
        "original_price": 1399.99,
        "imageUrl": "https://i02.appmifile.com/334_operator_sg/22/02/2024/d36105f6de5a716a1c0737352c2827be.png",
        "category": "Phone",
        "description": "Flagship Xiaomi with Leica cameras, premium design, and fast performance.",
        "rating": 4.6,
        "discount": 14
    },
    {
        "name": "Xiaomi 13T Pro",
        "price": 699.99,
        "original_price": 799.99,
        "imageUrl": "https://images.unsplash.com/photo-1567581935884-3349723552ca?w=500&h=500&fit=crop&crop=center",
        "category": "Phone",
        "description": "High-performance Xiaomi phone with fast charging and premium camera system.",
        "rating": 4.4,
        "discount": 13
    },
    {
        "name": "Xiaomi Redmi Note 13 Pro",
        "price": 349.99,
        "original_price": 399.99,
        "imageUrl": "https://images.unsplash.com/photo-1585060544812-6b45742d762f?w=500&h=500&fit=crop&crop=center",
        "category": "Phone",
        "description": "Affordable Xiaomi phone with great camera and long battery life.",
        "rating": 4.3,
        "discount": 13
    },
    {
        "name": "Xiaomi Poco X6 Pro",
        "price": 299.99,
        "original_price": 349.99,
        "imageUrl": "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=500&h=500&fit=crop&crop=center",
        "category": "Phone",
        "description": "Gaming-focused Xiaomi phone with powerful processor and fast display.",
        "rating": 4.2,
        "discount": 14
    },

    # LAPTOP CATEGORY (Dell, HP, Lenovo)
    {
        "name": "Dell XPS 13 Plus",
        "price": 1299.99,
        "original_price": 1499.99,
        "imageUrl": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&h=500&fit=crop&crop=center",
        "category": "Laptop",
        "description": "Premium Dell ultrabook with InfinityEdge display and Intel Core processors.",
        "rating": 4.6,
        "discount": 13
    },
    {
        "name": "Dell Inspiron 16",
        "price": 899.99,
        "original_price": 999.99,
        "imageUrl": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=500&h=500&fit=crop&crop=center",
        "category": "Laptop",
        "description": "Versatile Dell laptop for work and entertainment with large display.",
        "rating": 4.3,
        "discount": 10
    },
    {
        "name": "Dell G15 Gaming",
        "price": 1199.99,
        "original_price": 1399.99,
        "imageUrl": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500&h=500&fit=crop&crop=center",
        "category": "Laptop",
        "description": "Dell gaming laptop with dedicated graphics and high-refresh display.",
        "rating": 4.4,
        "discount": 14
    },
    {
        "name": "HP Spectre x360 14",
        "price": 1399.99,
        "original_price": 1599.99,
        "imageUrl": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=500&h=500&fit=crop&crop=center",
        "category": "Laptop",
        "description": "Premium HP convertible laptop with OLED display and stylus support.",
        "rating": 4.7,
        "discount": 13
    },
    {
        "name": "HP Pavilion 15",
        "price": 699.99,
        "original_price": 799.99,
        "imageUrl": "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=500&h=500&fit=crop&crop=center",
        "category": "Laptop",
        "description": "Reliable HP laptop for everyday computing with modern design.",
        "rating": 4.2,
        "discount": 13
    },
    {
        "name": "HP OMEN 16",
        "price": 1299.99,
        "original_price": 1499.99,
        "imageUrl": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=500&h=500&fit=crop&crop=center",
        "category": "Laptop",
        "description": "HP gaming laptop with powerful graphics and advanced cooling system.",
        "rating": 4.5,
        "discount": 13
    },
    {
        "name": "Lenovo ThinkPad X1 Carbon",
        "price": 1599.99,
        "original_price": 1799.99,
        "imageUrl": "https://images.unsplash.com/photo-1484788984921-03950022c9ef?w=500&h=500&fit=crop&crop=center",
        "category": "Laptop",
        "description": "Premium business laptop with legendary ThinkPad durability and performance.",
        "rating": 4.8,
        "discount": 11
    },
    {
        "name": "Lenovo IdeaPad 5 Pro",
        "price": 899.99,
        "original_price": 1099.99,
        "imageUrl": "https://no1computer.vn/images/products/2024/02/24/large/ideapad-5-pro-2023-rtx-4050-1_1700021341_1708402921_1708738877.jpg",
        "category": "Laptop",
        "description": "Versatile Lenovo laptop with 2.5K display and AMD Ryzen processors.",
        "rating": 4.4,
        "discount": 18
    },
    {
        "name": "Lenovo Legion 5 Pro",
        "price": 1399.99,
        "original_price": 1599.99,
        "imageUrl": "https://images.unsplash.com/photo-1587831990711-23ca6441447b?w=500&h=500&fit=crop&crop=center",
        "category": "Laptop",
        "description": "High-performance gaming laptop with RTX graphics and RGB keyboard.",
        "rating": 4.6,
        "discount": 13
    },
    {
        "name": "Lenovo Yoga 9i",
        "price": 1299.99,
        "original_price": 1499.99,
        "imageUrl": "https://mac24h.vn/images/detailed/95/Yoga-Slim-9-14ILL10-mac24h-1.png",
        "category": "Laptop",
        "description": "Premium convertible laptop with leather design and excellent audio system.",
        "rating": 4.5,
        "discount": 13
    },

    # WATCH CATEGORY (Apple, Samsung, Garmin)
    {
        "name": "Apple Watch Series 9",
        "price": 399.99,
        "original_price": 449.99,
        "imageUrl": "https://images.unsplash.com/photo-1551816230-ef5deaed4a26?w=500&h=500&fit=crop&crop=center",
        "category": "Watch",
        "description": "Advanced Apple smartwatch with health monitoring and fitness tracking.",
        "rating": 4.7,
        "discount": 11
    },
    {
        "name": "Apple Watch Ultra 2",
        "price": 799.99,
        "original_price": 899.99,
        "imageUrl": "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=500&h=500&fit=crop&crop=center",
        "category": "Watch",
        "description": "Rugged Apple watch for extreme sports with titanium case and precision GPS.",
        "rating": 4.8,
        "discount": 11
    },
    {
        "name": "Apple Watch SE",
        "price": 249.99,
        "original_price": 299.99,
        "imageUrl": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&h=500&fit=crop&crop=center",
        "category": "Watch",
        "description": "Affordable Apple smartwatch with essential features and fitness tracking.",
        "rating": 4.5,
        "discount": 17
    },
    {
        "name": "Samsung Galaxy Watch6",
        "price": 329.99,
        "original_price": 379.99,
        "imageUrl": "https://thetekcoffee.com/wp-content/uploads/2024/04/samsung-watch-6-44mm.jpg",
        "category": "Watch",
        "description": "Samsung smartwatch with comprehensive health tracking and long battery life.",
        "rating": 4.4,
        "discount": 13
    },
    {
        "name": "Samsung Galaxy Watch6 Classic",
        "price": 429.99,
        "original_price": 499.99,
        "imageUrl": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=500&h=500&fit=crop&crop=center",
        "category": "Watch",
        "description": "Premium Samsung smartwatch with rotating bezel and classic design.",
        "rating": 4.6,
        "discount": 14
    },
    {
        "name": "Samsung Galaxy Watch5 Pro",
        "price": 379.99,
        "original_price": 449.99,
        "imageUrl": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=500&h=500&fit=crop&crop=center",
        "category": "Watch",
        "description": "Rugged Samsung smartwatch with titanium case and extended battery life.",
        "rating": 4.5,
        "discount": 16
    },
    {
        "name": "Garmin Forerunner 965",
        "price": 599.99,
        "original_price": 699.99,
        "imageUrl": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=500&h=500&fit=crop&crop=center",
        "category": "Watch",
        "description": "Advanced Garmin running watch with AMOLED display and training metrics.",
        "rating": 4.7,
        "discount": 14
    },
    {
        "name": "Garmin Fenix 7X",
        "price": 799.99,
        "original_price": 899.99,
        "imageUrl": "https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=500&h=500&fit=crop&crop=center",
        "category": "Watch",
        "description": "Ultimate multisport GPS watch with solar charging and mapping features.",
        "rating": 4.8,
        "discount": 11
    },
    {
        "name": "Garmin Venu 3",
        "price": 449.99,
        "original_price": 499.99,
        "imageUrl": "https://images.unsplash.com/photo-1544117519-31a4b719223d?w=500&h=500&fit=crop&crop=center",
        "category": "Watch",
        "description": "Lifestyle GPS smartwatch with bright AMOLED display and health insights.",
        "rating": 4.6,
        "discount": 10
    },
    {
        "name": "Garmin Instinct 2X Solar",
        "price": 399.99,
        "original_price": 449.99,
        "imageUrl": "https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?w=500&h=500&fit=crop&crop=center",
        "category": "Watch",
        "description": "Rugged GPS watch with solar charging and military-grade durability.",
        "rating": 4.5,
        "discount": 11
    },

    # CAMERA CATEGORY (Sony, Fuji, Canon)
    {
        "name": "Sony Alpha 7R V",
        "price": 3899.99,
        "original_price": 4299.99,
        "imageUrl": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=500&h=500&fit=crop&crop=center",
        "category": "Camera",
        "description": "High-resolution full-frame mirrorless camera with 61MP sensor and advanced AI autofocus.",
        "rating": 4.8,
        "discount": 9
    },
    {
        "name": "Sony Alpha 7 IV",
        "price": 2499.99,
        "original_price": 2799.99,
        "imageUrl": "https://images.unsplash.com/photo-1606983340126-99ab4feaa64a?w=500&h=500&fit=crop&crop=center",
        "category": "Camera",
        "description": "Versatile full-frame camera perfect for photo and video with excellent image quality.",
        "rating": 4.7,
        "discount": 11
    },
    {
        "name": "Sony Alpha FX30",
        "price": 1799.99,
        "original_price": 1999.99,
        "imageUrl": "https://promotion.sony.com.vn:5001/storage/2024/10/04/FX3_t%20(1).png",
        "category": "Camera",
        "description": "Cinema-focused APS-C camera with 4K recording and professional video features.",
        "rating": 4.6,
        "discount": 10
    },
    {
        "name": "Fujifilm X-T5",
        "price": 1699.99,
        "original_price": 1899.99,
        "imageUrl": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=500&h=500&fit=crop&crop=center",
        "category": "Camera",
        "description": "High-resolution APS-C mirrorless camera with classic design and film simulations.",
        "rating": 4.7,
        "discount": 11
    },
    {
        "name": "Fujifilm X-H2S",
        "price": 2499.99,
        "original_price": 2799.99,
        "imageUrl": "https://product.hstatic.net/200000396087/product/fujifilm_frame_camera_x-h2s_body_3b8e11c917be421083e9c00580b0635c_grande.jpg",
        "category": "Camera",
        "description": "Professional APS-C camera with advanced video capabilities and fast shooting speeds.",
        "rating": 4.6,
        "discount": 11
    },
    {
        "name": "Fujifilm X100V",
        "price": 1399.99,
        "original_price": 1599.99,
        "imageUrl": "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=500&h=500&fit=crop&crop=center",
        "category": "Camera",
        "description": "Premium compact camera with fixed 35mm lens and hybrid viewfinder.",
        "rating": 4.8,
        "discount": 13
    },
    {
        "name": "Canon EOS R5",
        "price": 3899.99,
        "original_price": 4299.99,
        "imageUrl": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=500&h=500&fit=crop&crop=center",
        "category": "Camera",
        "description": "Professional full-frame mirrorless camera with 8K video and advanced image stabilization.",
        "rating": 4.8,
        "discount": 9
    },
    {
        "name": "Canon EOS R6 Mark II",
        "price": 2499.99,
        "original_price": 2799.99,
        "imageUrl": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=500&h=500&fit=crop&crop=center",
        "category": "Camera",
        "description": "Versatile full-frame camera with excellent low-light performance and fast autofocus.",
        "rating": 4.7,
        "discount": 11
    },
    {
        "name": "Canon EOS R10",
        "price": 979.99,
        "original_price": 1079.99,
        "imageUrl": "https://vn.canon/media/image/2022/05/22/3fdc4ae7f41d47fe9d1e01729527ef32_EOS+R10+Front+Body.png",
        "category": "Camera",
        "description": "Entry-level APS-C mirrorless camera perfect for beginners and content creators.",
        "rating": 4.4,
        "discount": 9
    },
    {
        "name": "Canon PowerShot G7X Mark III",
        "price": 749.99,
        "original_price": 849.99,
        "imageUrl": "https://m.media-amazon.com/images/I/71FxOAGHqtL.__AC_SX300_SY300_QL70_FMwebp_.jpg",
        "category": "Camera",
        "description": "Compact camera with 4K video, live streaming capabilities, and flip-up touchscreen.",
        "rating": 4.3,
        "discount": 12
    },

    # CAMPING GEAR CATEGORY (Nature Hike, Quechua, Coleman)
    {
        "name": "Nature Hike Cloud-Up 2 Tent",
        "price": 169.99,
        "original_price": 199.99,
        "imageUrl": "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=500&h=500&fit=crop&crop=center",
        "category": "Camping Gear",
        "description": "Ultralight 2-person tent with double-wall design, perfect for backpacking adventures.",
        "rating": 4.5,
        "discount": 15
    },
    {
        "name": "Nature Hike Ultralight Sleeping Pad",
        "price": 79.99,
        "original_price": 99.99,
        "imageUrl": "https://m.media-amazon.com/images/I/71XkNJI9QSL.__AC_SX300_SY300_QL70_FMwebp_.jpg",
        "category": "Camping Gear",
        "description": "Lightweight inflatable sleeping pad with R-value 4.2 for excellent insulation.",
        "rating": 4.4,
        "discount": 20
    },
    {
        "name": "Nature Hike Down Sleeping Bag",
        "price": 149.99,
        "original_price": 179.99,
        "imageUrl": "https://m.media-amazon.com/images/I/71dYJdShMgL.__AC_SX300_SY300_QL70_FMwebp_.jpg",
        "category": "Camping Gear",
        "description": "Compact down sleeping bag rated for 32°F, ideal for three-season camping.",
        "rating": 4.6,
        "discount": 17
    },
    {
        "name": "Quechua MH100 Hiking Backpack 60L",
        "price": 129.99,
        "original_price": 159.99,
        "imageUrl": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&h=500&fit=crop&crop=center",
        "category": "Camping Gear",
        "description": "Large capacity hiking backpack with adjustable fit and multiple compartments.",
        "rating": 4.3,
        "discount": 19
    },
    {
        "name": "Quechua NH100 Hiking Boots",
        "price": 89.99,
        "original_price": 109.99,
        "imageUrl": "https://rukminim2.flixcart.com/image/832/832/xif0q/shoe/j/4/7/-original-imagg3a8q7f56tdd.jpeg?q=70&crop=false",
        "category": "Camping Gear",
        "description": "Waterproof hiking boots with excellent grip and ankle support for mountain trails.",
        "rating": 4.2,
        "discount": 18
    },
    {
        "name": "Quechua Base Camp Tent 4.1",
        "price": 199.99,
        "original_price": 249.99,
        "imageUrl": "https://images.unsplash.com/photo-1487730116645-74489c95b41b?w=500&h=500&fit=crop&crop=center",
        "category": "Camping Gear",
        "description": "Family camping tent for 4 people with easy setup and weather protection.",
        "rating": 4.4,
        "discount": 20
    },
    {
        "name": "Coleman Sundome 6-Person Tent",
        "price": 159.99,
        "original_price": 189.99,
        "imageUrl": "https://images.unsplash.com/photo-1445308394109-4ec2920981b1?w=500&h=500&fit=crop&crop=center",
        "category": "Camping Gear",
        "description": "Spacious dome tent with WeatherTec system for reliable weather protection.",
        "rating": 4.1,
        "discount": 16
    },
    {
        "name": "Coleman Dual Fuel Stove",
        "price": 119.99,
        "original_price": 139.99,
        "imageUrl": "https://images.unsplash.com/photo-1511593358241-7eea1f3c84e5?w=500&h=500&fit=crop&crop=center",
        "category": "Camping Gear",
        "description": "Powerful two-burner stove that runs on Coleman fuel or unleaded gasoline.",
        "rating": 4.5,
        "discount": 14
    },
    {
        "name": "Coleman Xtreme 70-Quart Cooler",
        "price": 89.99,
        "original_price": 109.99,
        "imageUrl": "https://m.media-amazon.com/images/I/71XYt4u8-vL.__AC_SX300_SY300_QL70_FMwebp_.jpg?w=500&h=500&fit=crop&crop=center",
        "category": "Camping Gear",
        "description": "Large capacity cooler with Xtreme technology for 5-day ice retention.",
        "rating": 4.3,
        "discount": 18
    },
    {
        "name": "Coleman Rechargeable LED Lantern",
        "price": 49.99,
        "original_price": 59.99,
        "imageUrl": "https://newellbrands.imgix.net/b4cd0864-ca99-3be0-bbb8-8d7dc07d51a2/b4cd0864-ca99-3be0-bbb8-8d7dc07d51a2.tif?auto=format,compress&w=500",
        "category": "Camping Gear",
        "description": "Bright LED lantern with USB charging port and 300-hour runtime on low setting.",
        "rating": 4.4,
        "discount": 17
    }
]

async def clear_existing_products():
    """Clear all existing products from Firestore"""
    db = get_firestore_db()
    products_ref = db.collection('products')
    
    print("[INFO] Clearing existing products...")
    
    # Get all existing products
    docs = products_ref.stream()
    batch = db.batch()
    count = 0
    
    for doc in docs:
        batch.delete(doc.reference)
        count += 1
        
        # Firestore batch limit is 500 operations
        if count % 500 == 0:
            await asyncio.to_thread(batch.commit)
            batch = db.batch()
    
    if count % 500 != 0:
        await asyncio.to_thread(batch.commit)
    
    print(f"[SUCCESS] Cleared {count} existing products")

async def upload_products():
    """Upload all products to Firestore"""
    db = get_firestore_db()
    products_ref = db.collection('products')
    
    print("[INFO] Starting product upload...")
    print(f"[INFO] Total products to upload: {len(PRODUCTS_DATA)}")
    
    # Upload products in batches
    batch_size = 50
    product_counter = 1
    
    for i in range(0, len(PRODUCTS_DATA), batch_size):
        batch = db.batch()
        batch_products = PRODUCTS_DATA[i:i + batch_size]
        
        for product_data in batch_products:
            # Prepare product document with integer ID like migrate_data.py
            try:
                product_dict = product_data.copy()
                product_dict['id'] = product_counter
                product_dict['created_at'] = time.time()
                product_dict['updated_at'] = time.time()
                
                # Ensure required fields have defaults
                if 'rating' not in product_dict:
                    product_dict['rating'] = 4.0
                if 'discount' not in product_dict:
                    product_dict['discount'] = 0
                
                # Validate with ProductCreate (without the extra fields)
                product_create = ProductCreate(**product_data)
                
                # Add to batch with specific document ID
                doc_ref = products_ref.document(str(product_counter))
                batch.set(doc_ref, product_dict)
                
                product_counter += 1
                
            except Exception as e:
                print(f"[ERROR] Error processing product {product_data.get('name', 'Unknown')}: {e}")
                continue
        
        # Commit the batch
        await asyncio.to_thread(batch.commit)
        print(f"[SUCCESS] Uploaded batch {i//batch_size + 1}/{(len(PRODUCTS_DATA) + batch_size - 1)//batch_size}")
        
        # Small delay to avoid rate limiting
        await asyncio.sleep(0.5)
    
    print("[SUCCESS] All products uploaded successfully!")

class ChromaDBEmbedder:
    """Class to handle ChromaDB embedding functionality"""
    
    def __init__(self):
        """Initialize the ChromaDB embedder"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.embedding_model = "text-embedding-3-small"
        
        if self.api_key:
            self.openai_client = openai.OpenAI(api_key=self.api_key)
            print(f"[SUCCESS] OpenAI client initialized")
        else:
            print("[ERROR] OpenAI API key not found in environment variables")
            return
        
        # Initialize ChromaDB client
        try:
            self.chroma_client = chromadb.PersistentClient(
                path="./chroma_db",
                settings=Settings(anonymized_telemetry=False)
            )
            print("[SUCCESS] ChromaDB client initialized")
        except Exception as e:
            print(f"[ERROR] ChromaDB initialization failed: {e}")
            return
        
        # Initialize collection
        self._initialize_collection()
    
    def _initialize_collection(self):
        """Initialize or get the ChromaDB collection"""
        try:
            # Delete existing collection if it exists
            try:
                self.chroma_client.delete_collection("products_embeddings")
                print("[INFO] Deleted existing ChromaDB collection")
            except Exception:
                pass  # Collection didn't exist
            
            # Create new collection with the correct name expected by AI service
            self.collection = self.chroma_client.create_collection(
                name="products_embeddings",
                metadata={
                    "hnsw:space": "cosine", 
                    "description": "E-commerce product embeddings",
                    "embedding_model": "text-embedding-3-small",
                    "embedding_dimensions": 1536
                },
                embedding_function=None  # We provide our own embeddings
            )
            print("[SUCCESS] Created new ChromaDB collection 'products_embeddings'")
            
        except Exception as e:
            print(f"[ERROR] Collection initialization failed: {e}")
            raise e
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"[ERROR] Embedding generation failed: {e}")
            return []
    
    def prepare_product_text(self, product_data: Dict) -> str:
        """Prepare enhanced product text for embedding with detailed keywords"""
        # Get enhanced keywords based on product name and category using shared utility
        keywords = get_product_keywords_from_dict(product_data)
        
        text_parts = [
            f"Product: {product_data['name']}",
            f"Category: {product_data['category']}",
            f"Price: ${product_data['price']}"
        ]
        
        # Add enhanced keywords for better search
        if keywords:
            text_parts.append(f"Features: {' '.join(keywords)}")
        
        if product_data.get('description'):
            text_parts.append(f"Description: {product_data['description']}")
        
        if product_data.get('rating'):
            text_parts.append(f"Rating: {product_data['rating']}/5")
        
        return " | ".join(text_parts)
    
    def prepare_product_metadata(self, product_data: Dict, product_id: str) -> Dict[str, Any]:
        """Prepare product metadata for ChromaDB"""
        metadata = {
            "id": product_id,
            "name": product_data["name"],
            "category": product_data["category"],
            "price": float(product_data["price"])
        }
        
        # Add optional fields
        if product_data.get('original_price'):
            metadata["original_price"] = float(product_data['original_price'])
        
        if product_data.get('rating'):
            metadata["rating"] = float(product_data['rating'])
        
        if product_data.get('discount'):
            metadata["discount"] = float(product_data['discount'])
        
        if product_data.get('imageUrl'):
            metadata["imageUrl"] = product_data['imageUrl']
        
        if product_data.get('description'):
            metadata["description"] = product_data['description']
        
        return metadata

async def generate_and_store_embeddings():
    """Generate embeddings and store them in ChromaDB"""
    print("[INFO] Starting embedding generation and ChromaDB storage...")
    
    # Initialize ChromaDB embedder
    try:
        embedder = ChromaDBEmbedder()
        if not hasattr(embedder, 'openai_client') or not hasattr(embedder, 'collection'):
            print("[ERROR] ChromaDB embedder initialization failed")
            return
    except Exception as e:
        print(f"[ERROR] Failed to initialize embedder: {e}")
        return
    
    # Get products from Firebase
    db = get_firestore_db()
    products_ref = db.collection('products')
    docs = products_ref.stream()
    
    products_data = []
    product_ids = []
    for doc in docs:
        products_data.append(doc.to_dict())
        product_ids.append(doc.id)
    
    if not products_data:
        print("[WARNING] No products found in Firebase")
        return
    
    print(f"[INFO] Found {len(products_data)} products to embed")
    
    # Process products for embeddings
    successful_embeddings = 0
    failed_embeddings = 0
    
    for i, (product_data, product_id) in enumerate(zip(products_data, product_ids), 1):
        try:
            print(f"[INFO] Processing product {i}/{len(products_data)}: {product_data['name']}")
            
            # Prepare text for embedding
            text = embedder.prepare_product_text(product_data)
            
            # Get embedding
            embedding = embedder.get_embedding(text)
            
            if not embedding:
                print(f"[ERROR] Failed to get embedding for {product_data['name']}")
                failed_embeddings += 1
                continue
            
            # Prepare metadata - use the id field from product_data
            metadata = embedder.prepare_product_metadata(product_data, str(product_data['id']))
            
            # Add to ChromaDB
            embedder.collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata],
                ids=[f"product_{product_data['id']}"]
            )
            
            successful_embeddings += 1
            print(f"[SUCCESS] Added {product_data['name']} to ChromaDB")
            
            # Small delay to respect rate limits
            await asyncio.sleep(0.3)
            
        except Exception as e:
            print(f"[ERROR] Failed to process {product_data.get('name', 'Unknown')}: {e}")
            failed_embeddings += 1
            continue
    
    # Print results
    print("\n" + "=" * 50)
    print("[EMBEDDING RESULTS]")
    print(f"  Successful: {successful_embeddings}")
    print(f"  Failed: {failed_embeddings}")
    print(f"  Total: {len(products_data)}")
    
    # Verify ChromaDB collection
    try:
        collection_count = embedder.collection.count()
        print(f"  ChromaDB items: {collection_count}")
        
        if collection_count > 0:
            # Test query
            test_results = embedder.collection.query(
                query_texts=["phone"],
                n_results=3
            )
            print(f"  Test query results: {len(test_results['ids'][0])}")
    except Exception as e:
        print(f"  [ERROR] Verification failed: {e}")
    
    print("=" * 50)

async def verify_upload():
    """Verify that products were uploaded correctly"""
    db = get_firestore_db()
    products_ref = db.collection('products')
    
    print("[INFO] Verifying upload...")
    
    # Count products by category
    categories = {}
    docs = products_ref.stream()
    total_count = 0
    
    for doc in docs:
        data = doc.to_dict()
        category = data.get('category', 'Unknown')
        categories[category] = categories.get(category, 0) + 1
        total_count += 1
    
    print(f"[INFO] Total products in database: {total_count}")
    print("[INFO] Products by category:")
    for category, count in sorted(categories.items()):
        print(f"   {category}: {count} products")
    
    # Verify we have the expected categories
    expected_categories = ["Phone", "Laptop", "Watch", "Camera", "Camping Gear"]
    for category in expected_categories:
        if category not in categories:
            print(f"[WARNING] Missing category {category}")
        elif categories[category] != 10:
            print(f"[WARNING] Category {category} has {categories[category]} products, expected 10")
        else:
            print(f"[SUCCESS] Category {category}: {categories[category]} products (correct)")

async def main():
    """Main migration function"""
    print("[START] Starting Data Migration v2 with ChromaDB embeddings...")
    print("=" * 65)
    
    try:
        # Clear existing products
        await clear_existing_products()
        
        print()
        
        # Upload new products to Firebase
        await upload_products()
        
        print()
        
        # Generate embeddings and store in ChromaDB
        await generate_and_store_embeddings()
        
        print()
        
        # Verify upload
        await verify_upload()
        
        print()
        print("=" * 65)
        print("[SUCCESS] Migration v2 completed successfully!")
        print("[INFO] Completed steps:")
        print("  - Uploaded 50 products to Firebase Firestore")
        print("  - Generated embeddings using OpenAI API")
        print("  - Stored embeddings in ChromaDB for vector search")
        print("  - Products are now ready for AI-powered recommendations")
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
