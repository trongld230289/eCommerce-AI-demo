#!/usr/bin/env python3
"""
Data Migration Script for BEv2
Populates Neo4j database with initial product data
"""

import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_config import get_neo4j_driver

def get_sample_products() -> List[Dict[str, Any]]:
    """Get sample products data"""
    return [
        {
            'id': 1,
            'name': 'iPhone 15 Pro',
            'brand': 'Apple',
            'category': 'Smartphones',
            'price': 1200.00,
            'description': 'Latest iPhone with A17 Pro chip and titanium design',
            'stock': 50,
            'rating': 4.8,
            'reviews': 1250,
            'featured': True,
            'image_url': 'https://example.com/iphone15pro.jpg',
            'weeklySales': 85,
            'weeklyViews': 2340
        },
        {
            'id': 2,
            'name': 'Samsung Galaxy S24 Ultra',
            'brand': 'Samsung',
            'category': 'Smartphones',
            'price': 899.99,
            'description': 'Premium Samsung smartphone with S Pen and advanced camera',
            'stock': 25,
            'rating': 4.6,
            'reviews': 890,
            'featured': True,
            'image_url': 'https://example.com/galaxy-s24-ultra.jpg',
            'weeklySales': 65,
            'weeklyViews': 1890
        },
        {
            'id': 3,
            'name': 'Dell XPS 13',
            'brand': 'Dell',
            'category': 'Laptops',
            'price': 1800.00,
            'description': 'Ultra-portable laptop with Intel Core i7 and 16GB RAM',
            'stock': 15,
            'rating': 4.5,
            'reviews': 560,
            'featured': False,
            'image_url': 'https://example.com/dell-xps-13.jpg',
            'weeklySales': 12,
            'weeklyViews': 780
        },
        {
            'id': 4,
            'name': 'MacBook Air M3',
            'brand': 'Apple',
            'category': 'Laptops',
            'price': 2400.00,
            'description': 'Apple MacBook Air with M3 chip, 13-inch display',
            'stock': 12,
            'rating': 4.9,
            'reviews': 750,
            'featured': True,
            'image_url': 'https://example.com/macbook-air-m3.jpg',
            'weeklySales': 28,
            'weeklyViews': 1560
        },
        {
            'id': 5,
            'name': 'Sony WH-1000XM5',
            'brand': 'Sony',
            'category': 'Headphones',
            'price': 399.99,
            'description': 'Premium noise-canceling wireless headphones',
            'stock': 30,
            'rating': 4.7,
            'reviews': 1180,
            'featured': True,
            'image_url': 'https://example.com/sony-wh1000xm5.jpg',
            'weeklySales': 45,
            'weeklyViews': 1200
        },
        {
            'id': 6,
            'name': 'iPad Pro 12.9"',
            'brand': 'Apple',
            'category': 'Tablets',
            'price': 1699.99,
            'description': 'Professional iPad with M2 chip and Liquid Retina XDR display',
            'stock': 18,
            'rating': 4.8,
            'reviews': 920,
            'featured': False,
            'image_url': 'https://example.com/ipad-pro-129.jpg',
            'weeklySales': 22,
            'weeklyViews': 980
        },
        {
            'id': 7,
            'name': 'Samsung Galaxy Watch 6',
            'brand': 'Samsung',
            'category': 'Smart Watches',
            'price': 329.99,
            'description': 'Advanced smartwatch with health monitoring and GPS',
            'stock': 40,
            'rating': 4.4,
            'reviews': 680,
            'featured': False,
            'image_url': 'https://example.com/galaxy-watch-6.jpg',
            'weeklySales': 18,
            'weeklyViews': 650
        },
        {
            'id': 8,
            'name': 'Canon EOS R6 Mark II',
            'brand': 'Canon',
            'category': 'Cameras',
            'price': 4500.00,
            'description': 'Professional mirrorless camera with 24.2MP full-frame sensor',
            'stock': 8,
            'rating': 4.9,
            'reviews': 340,
            'featured': False,
            'image_url': 'https://example.com/canon-eos-r6-ii.jpg',
            'weeklySales': 3,
            'weeklyViews': 450
        },
        {
            'id': 9,
            'name': 'Nintendo Switch OLED',
            'brand': 'Nintendo',
            'category': 'Gaming Consoles',
            'price': 800.00,
            'description': 'Gaming console with 7-inch OLED screen and enhanced audio',
            'stock': 35,
            'rating': 4.6,
            'reviews': 1580,
            'featured': True,
            'image_url': 'https://example.com/nintendo-switch-oled.jpg',
            'weeklySales': 52,
            'weeklyViews': 1890
        },
        {
            'id': 10,
            'name': 'LG OLED C3 55"',
            'brand': 'LG',
            'category': 'TVs',
            'price': 3500.00,
            'description': '55-inch OLED 4K Smart TV with Dolby Vision and webOS',
            'stock': 10,
            'rating': 4.7,
            'reviews': 480,
            'featured': False,
            'image_url': 'https://example.com/lg-oled-c3-55.jpg',
            'weeklySales': 8,
            'weeklyViews': 720
        },
        {
            'id': 11,
            'name': 'Wireless Headphones',
            'brand': 'AudioTech',
            'category': 'Electronics',
            'price': 199.99,
            'description': 'High-quality wireless headphones with noise cancellation',
            'stock': 45,
            'rating': 4.3,
            'reviews': 523,
            'featured': False,
            'image_url': 'https://example.com/wireless-headphones.jpg',
            'weeklySales': 15,
            'weeklyViews': 890
        },
        {
            'id': 12,
            'name': 'Smart Watch',
            'brand': 'TechWatch',
            'category': 'Electronics',
            'price': 299.99,
            'description': 'Feature-rich smartwatch with fitness tracking',
            'stock': 30,
            'rating': 4.2,
            'reviews': 234,
            'featured': False,
            'image_url': 'https://example.com/smart-watch.jpg',
            'weeklySales': 25,
            'weeklyViews': 1120
        },
        {
            'id': 13,
            'name': 'Gaming Laptop',
            'brand': 'GameMaster',
            'category': 'Electronics',
            'price': 999.99,
            'description': 'High-performance gaming laptop with RTX graphics',
            'stock': 20,
            'rating': 4.5,
            'reviews': 156,
            'featured': True,
            'image_url': 'https://example.com/gaming-laptop.jpg',
            'weeklySales': 8,
            'weeklyViews': 567
        },
        {
            'id': 14,
            'name': 'Smartphone Pro',
            'brand': 'PhoneTech',
            'category': 'Electronics',
            'price': 799.99,
            'description': 'Premium smartphone with advanced camera system',
            'stock': 35,
            'rating': 4.4,
            'reviews': 789,
            'featured': False,
            'image_url': 'https://example.com/smartphone-pro.jpg',
            'weeklySales': 42,
            'weeklyViews': 1340
        },
        {
            'id': 15,
            'name': 'Portable Bluetooth Speaker',
            'brand': 'SoundWave',
            'category': 'Electronics',
            'price': 79.99,
            'description': 'Compact Bluetooth speaker with excellent sound quality',
            'stock': 50,
            'rating': 4.1,
            'reviews': 445,
            'featured': False,
            'image_url': 'https://example.com/bluetooth-speaker.jpg',
            'weeklySales': 38,
            'weeklyViews': 980
        },
        {
            'id': 16,
            'name': 'RGB Gaming Mouse',
            'brand': 'GamerGear',
            'category': 'Electronics',
            'price': 49.99,
            'description': 'Precision gaming mouse with customizable RGB lighting',
            'stock': 75,
            'rating': 4.3,
            'reviews': 320,
            'featured': False,
            'image_url': 'https://example.com/rgb-gaming-mouse.jpg',
            'weeklySales': 55,
            'weeklyViews': 750
        },
        {
            'id': 17,
            'name': 'Mechanical Gaming Keyboard',
            'brand': 'KeyMaster',
            'category': 'Electronics',
            'price': 129.99,
            'description': 'Mechanical keyboard with tactile switches and RGB backlighting',
            'stock': 40,
            'rating': 4.6,
            'reviews': 280,
            'featured': False,
            'image_url': 'https://example.com/mechanical-keyboard.jpg',
            'weeklySales': 30,
            'weeklyViews': 620
        },
        {
            'id': 18,
            'name': 'iPad Tablet',
            'brand': 'TabletPro',
            'category': 'Electronics',
            'price': 599.99,
            'description': '10.2-inch tablet with high-resolution display',
            'stock': 25,
            'rating': 4.2,
            'reviews': 190,
            'featured': False,
            'image_url': 'https://example.com/ipad-tablet.jpg',
            'weeklySales': 20,
            'weeklyViews': 450
        }
    ]

def clear_database(driver):
    """Clear all existing data in Neo4j"""
    print("🧹 Clearing existing Neo4j data...")
    try:
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("✅ Database cleared")
        return True
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False

def create_products(driver, products: List[Dict[str, Any]]):
    """Create product nodes and relationships in Neo4j"""
    print(f"📦 Creating {len(products)} products...")
    
    created_count = 0
    brands = set()
    categories = set()
    
    try:
        with driver.session() as session:
            for product in products:
                # Create product node
                create_query = """
                CREATE (p:Product {
                    id: $id,
                    name: $name,
                    brand: $brand,
                    category: $category,
                    price: $price,
                    description: $description,
                    stock: $stock,
                    rating: $rating,
                    reviews: $reviews,
                    featured: $featured,
                    image_url: $image_url,
                    weeklySales: $weeklySales,
                    weeklyViews: $weeklyViews,
                    created_at: $created_at,
                    updated_at: $updated_at
                })
                RETURN p
                """
                
                params = {
                    'id': product['id'],
                    'name': product['name'],
                    'brand': product['brand'],
                    'category': product['category'],
                    'price': float(product['price']),
                    'description': product['description'],
                    'stock': int(product['stock']),
                    'rating': float(product['rating']),
                    'reviews': int(product['reviews']),
                    'featured': bool(product['featured']),
                    'image_url': product['image_url'],
                    'weeklySales': int(product.get('weeklySales', 0)),
                    'weeklyViews': int(product.get('weeklyViews', 0)),
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                session.run(create_query, params)
                created_count += 1
                
                brands.add(product['brand'])
                categories.add(product['category'])
                
                print(f"✓ Created: {product['name']}")
        
        print(f"\n🏷️ Creating {len(brands)} brand nodes...")
        with driver.session() as session:
            for brand in brands:
                session.run("MERGE (b:Brand {name: $name})", {'name': brand})
                print(f"✓ Brand: {brand}")
        
        print(f"\n📁 Creating {len(categories)} category nodes...")
        with driver.session() as session:
            for category in categories:
                session.run("MERGE (c:Category {name: $name})", {'name': category})
                print(f"✓ Category: {category}")
        
        print(f"\n🔗 Creating relationships...")
        with driver.session() as session:
            for product in products:
                # Create brand relationship
                session.run("""
                    MATCH (p:Product {id: $product_id})
                    MATCH (b:Brand {name: $brand_name})
                    MERGE (p)-[:MANUFACTURED_BY]->(b)
                """, {'product_id': product['id'], 'brand_name': product['brand']})
                
                # Create category relationship
                session.run("""
                    MATCH (p:Product {id: $product_id})
                    MATCH (c:Category {name: $category_name})
                    MERGE (p)-[:BELONGS_TO]->(c)
                """, {'product_id': product['id'], 'category_name': product['category']})
        
        print(f"✅ Migration completed successfully!")
        print(f"   📦 Products: {created_count}")
        print(f"   🏷️ Brands: {len(brands)}")
        print(f"   📁 Categories: {len(categories)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating products: {e}")
        return False

def create_indexes(driver):
    """Create useful indexes in Neo4j"""
    print("\n🔧 Creating indexes...")
    
    indexes = [
        "CREATE INDEX product_id_index IF NOT EXISTS FOR (p:Product) ON (p.id)",
        "CREATE INDEX product_name_index IF NOT EXISTS FOR (p:Product) ON (p.name)",
        "CREATE INDEX product_category_index IF NOT EXISTS FOR (p:Product) ON (p.category)",
        "CREATE INDEX product_brand_index IF NOT EXISTS FOR (p:Product) ON (p.brand)",
        "CREATE INDEX brand_name_index IF NOT EXISTS FOR (b:Brand) ON (b.name)",
        "CREATE INDEX category_name_index IF NOT EXISTS FOR (c:Category) ON (c.name)"
    ]
    
    try:
        with driver.session() as session:
            for index_query in indexes:
                try:
                    session.run(index_query)
                    print("✓ Index created")
                except Exception as e:
                    print(f"⚠️ Index warning: {e}")
        
        print("✅ Indexes created")
        return True
        
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")
        return False

def verify_migration(driver):
    """Verify the migration results"""
    print("\n🔍 Verifying migration...")
    
    try:
        with driver.session() as session:
            # Count nodes
            product_result = session.run("MATCH (p:Product) RETURN count(p) as count")
            product_count = product_result.single()['count']
            
            brand_result = session.run("MATCH (b:Brand) RETURN count(b) as count")
            brand_count = brand_result.single()['count']
            
            category_result = session.run("MATCH (c:Category) RETURN count(c) as count")
            category_count = category_result.single()['count']
            
            # Count relationships
            rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = rel_result.single()['count']
            
            print(f"📊 Migration Results:")
            print(f"   📦 Products: {product_count}")
            print(f"   🏷️ Brands: {brand_count}")
            print(f"   📁 Categories: {category_count}")
            print(f"   🔗 Relationships: {rel_count}")
            
            # Show sample data
            print(f"\n📋 Sample products:")
            sample_result = session.run("""
                MATCH (p:Product)-[:MANUFACTURED_BY]->(b:Brand)
                MATCH (p)-[:BELONGS_TO]->(c:Category)
                RETURN p.name as product, b.name as brand, c.name as category
                LIMIT 5
            """)
            
            for i, record in enumerate(sample_result, 1):
                print(f"   {i}. {record['product']} by {record['brand']} in {record['category']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying migration: {e}")
        return False

def main():
    print("🚀 Data Migration for BEv2")
    print("=" * 50)
    print("📍 Neo4j Server: neo4j://203.145.46.236:30687")
    print("👤 Neo4j User: neo4j")
    print()
    
    try:
        # Get Neo4j driver
        driver = get_neo4j_driver()
        
        # Test connection
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            result.single()
        
        print("✅ Connected to Neo4j successfully")
        
        # Ask user for confirmation
        print("\n⚠️  WARNING: This will delete all existing data in Neo4j")
        choice = input("Continue with migration? (y/n): ").lower().strip()
        
        if choice not in ['y', 'yes']:
            print("❌ Migration cancelled by user")
            return
        
        # Step 1: Clear database
        if not clear_database(driver):
            return
        
        # Step 2: Get sample products
        products = get_sample_products()
        
        # Step 3: Create products
        if not create_products(driver, products):
            return
        
        # Step 4: Create indexes
        if not create_indexes(driver):
            return
        
        # Step 5: Verify migration
        if not verify_migration(driver):
            return
        
        print("\n" + "=" * 50)
        print("✨ Migration completed successfully!")
        print("🎯 Neo4j database is ready for BEv2")
        print("🚀 You can now start the BEv2 server on port 8010")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        # Close connection
        from database_config import close_neo4j_connection
        close_neo4j_connection()

if __name__ == "__main__":
    main()
