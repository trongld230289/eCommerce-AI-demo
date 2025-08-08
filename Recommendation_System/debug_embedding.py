#!/usr/bin/env python3
"""
Debug script for semantic search embedding issues
"""

import requests
import json

def debug_embedding_process():
    """Debug the embedding process step by step"""
    
    print("🔍 Debugging Embedding Process")
    print("=" * 40)
    
    # 1. Check if we can get products from backend
    print("\n1. Fetching products from backend...")
    try:
        response = requests.get("http://localhost:8000/products", timeout=5)
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Got {len(products)} products from backend")
            
            # Check first product structure
            if products:
                first_product = products[0]
                print(f"📋 First product structure:")
                print(f"   ID: {first_product.get('id')}")
                print(f"   Name: {first_product.get('name')}")
                print(f"   Category: {first_product.get('category')}")
                print(f"   Brand: {first_product.get('brand')}")
                print(f"   Description: {first_product.get('description', '')[:50]}...")
                
                # Test embedding text creation
                text_parts = []
                if first_product.get("name"):
                    text_parts.append(first_product["name"])
                if first_product.get("category"):
                    text_parts.append(first_product["category"])
                if first_product.get("brand"):
                    text_parts.append(first_product["brand"])
                if first_product.get("description"):
                    text_parts.append(first_product["description"])
                
                embedding_text = " ".join(text_parts).lower()
                print(f"🔤 Generated embedding text: '{embedding_text[:100]}...'")
                
        else:
            print(f"❌ Failed to get products: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Error fetching products: {e}")
        return
    
    # 2. Test recommendation service product cache
    print("\n2. Testing recommendation service product cache...")
    try:
        response = requests.get("http://localhost:8001/search/status")
        if response.status_code == 200:
            status = response.json()
            print(f"📊 Recommendation service status:")
            print(f"   Chroma Available: {status['chroma_available']}")
            print(f"   Embeddings Initialized: {status['embeddings_initialized']}")
            print(f"   Products in Cache: {status['products_in_cache']}")
        else:
            print(f"❌ Failed to get status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting status: {e}")
    
    # 3. Test manual embedding
    print("\n3. Testing manual embedding initialization...")
    try:
        response = requests.post("http://localhost:8001/products/embed", 
                               json={"force_refresh": True})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Embedding successful:")
            print(f"   Message: {result['message']}")
            print(f"   Total Products: {result['total_products']}")
        else:
            print(f"❌ Embedding failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error during embedding: {e}")
    
    # 4. Test simple semantic search
    print("\n4. Testing semantic search...")
    try:
        search_data = {
            "query": "iPhone",
            "limit": 3,
            "min_similarity": 0.1
        }
        
        response = requests.post("http://localhost:8001/search/semantic", 
                               json=search_data)
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Search successful:")
            print(f"   Query: {results['query']}")
            print(f"   Results: {results['count']}")
            
            for i, result in enumerate(results['results'][:2], 1):
                product = result['product_data']
                similarity = result['similarity_score']
                print(f"   {i}. {product['name']} (Similarity: {similarity:.3f})")
                
        else:
            print(f"❌ Search failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error during search: {e}")

if __name__ == "__main__":
    debug_embedding_process()
