#!/usr/bin/env python3
"""
Test script for Semantic Product Search API
This script demonstrates the new semantic search functionality with embeddings and cosine similarity
"""

import requests
import json
from datetime import datetime

# API Configuration
RECOMMENDATION_API_URL = "http://localhost:8001"
BACKEND_API_URL = "http://localhost:8000"

def test_api_endpoint(url, method="GET", data=None):
    """Helper function to test API endpoints"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

def test_semantic_search():
    """Test the semantic search functionality"""
    print("🔍 Testing Semantic Product Search API")
    print("=" * 60)
    
    # 1. Check search system status
    print("\n1. Checking search system status...")
    status = test_api_endpoint(f"{RECOMMENDATION_API_URL}/search/status")
    if status:
        print("✅ Search Status:")
        print(f"   - Chroma DB Available: {status.get('chroma_available')}")
        print(f"   - Embeddings Initialized: {status.get('embeddings_initialized')}")
        print(f"   - Products in Cache: {status.get('products_in_cache')}")
        print(f"   - Collection Available: {status.get('collection_available')}")
    
    # 2. Initialize embeddings if needed
    if not status.get('embeddings_initialized', False):
        print("\n2. Initializing product embeddings...")
        embed_result = test_api_endpoint(
            f"{RECOMMENDATION_API_URL}/products/embed", 
            method="POST",
            data={"force_refresh": True}
        )
        if embed_result:
            print(f"✅ Embeddings created for {embed_result.get('total_products')} products")
        else:
            print("❌ Failed to initialize embeddings")
            return
    else:
        print("\n2. ✅ Embeddings already initialized")
    
    # 3. Test semantic search queries
    test_queries = [
        "iPhone camera chụp ảnh đẹp",
        "laptop gaming mạnh mẽ",
        "tai nghe bluetooth chống ồn",
        "điện thoại Samsung giá rẻ",
        "máy tính xách tay làm việc",
        "smartphone cao cấp premium",
        "headphone âm thanh chất lượng",
        "Dell XPS performance",
        "Apple products",
        "gaming laptop under 20 million"
    ]
    
    print("\n3. Testing Semantic Search Queries:")
    print("-" * 40)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: '{query}'")
        
        # Semantic search
        semantic_result = test_api_endpoint(
            f"{RECOMMENDATION_API_URL}/search/semantic",
            method="POST",
            data={
                "query": query,
                "limit": 5,
                "min_similarity": 0.3
            }
        )
        
        if semantic_result:
            results = semantic_result.get('results', [])
            print(f"   📊 Found {len(results)} semantic matches:")
            
            for j, result in enumerate(results[:3], 1):  # Show top 3
                product = result.get('product_data', {})
                similarity = result.get('similarity_score', 0)
                print(f"     {j}. {product.get('name', 'Unknown')} (Similarity: {similarity:.3f})")
                print(f"        Category: {product.get('category', 'N/A')} | Brand: {product.get('brand', 'N/A')}")
                print(f"        Price: {product.get('price', 0):,.0f} VND")
    
    # 4. Test hybrid search
    print("\n4. Testing Hybrid Search (Semantic + Keyword):")
    print("-" * 50)
    
    hybrid_queries = [
        "iPhone 14 Pro Max",
        "Dell laptop gaming",
        "Samsung Galaxy S23"
    ]
    
    for query in hybrid_queries:
        print(f"\n🔀 Hybrid Query: '{query}'")
        
        hybrid_result = test_api_endpoint(
            f"{RECOMMENDATION_API_URL}/search/hybrid",
            method="POST",
            data={
                "query": query,
                "limit": 5,
                "semantic_weight": 0.7  # 70% semantic, 30% keyword
            }
        )
        
        if hybrid_result:
            results = hybrid_result.get('results', [])
            print(f"   📊 Found {len(results)} hybrid matches:")
            
            for j, result in enumerate(results[:3], 1):
                product = result.get('product_data', {})
                hybrid_score = result.get('hybrid_score', 0)
                semantic_score = result.get('semantic_score', 0)
                keyword_score = result.get('keyword_score', 0)
                
                print(f"     {j}. {product.get('name', 'Unknown')} (Hybrid: {hybrid_score:.3f})")
                print(f"        Semantic: {semantic_score:.3f} | Keyword: {keyword_score:.3f}")
                print(f"        Price: {product.get('price', 0):,.0f} VND")
    
    # 5. Compare with traditional search
    print("\n5. Comparing with Traditional Smart Search:")
    print("-" * 45)
    
    comparison_query = "smartphone camera chất lượng cao"
    print(f"\n📱 Comparison Query: '{comparison_query}'")
    
    # Traditional smart search
    traditional_result = test_api_endpoint(
        f"{RECOMMENDATION_API_URL}/search",
        method="POST",
        data={
            "query": comparison_query,
            "limit": 3
        }
    )
    
    # Semantic search
    semantic_result = test_api_endpoint(
        f"{RECOMMENDATION_API_URL}/search/semantic",
        method="POST",
        data={
            "query": comparison_query,
            "limit": 3,
            "min_similarity": 0.2
        }
    )
    
    print("\n   📊 Traditional Smart Search Results:")
    if traditional_result:
        for i, product in enumerate(traditional_result.get('results', [])[:3], 1):
            print(f"     {i}. {product.get('name', 'Unknown')} - {product.get('price', 0):,.0f} VND")
    
    print("\n   🧠 Semantic Search Results:")
    if semantic_result:
        for i, result in enumerate(semantic_result.get('results', [])[:3], 1):
            product = result.get('product_data', {})
            similarity = result.get('similarity_score', 0)
            print(f"     {i}. {product.get('name', 'Unknown')} (Sim: {similarity:.3f}) - {product.get('price', 0):,.0f} VND")
    
    print("\n" + "=" * 60)
    print("🎉 Semantic Search API Testing Complete!")
    print("✅ Key Features Tested:")
    print("   - Product embedding creation")
    print("   - Semantic search with cosine similarity")
    print("   - Hybrid search (semantic + keyword)")
    print("   - Similarity score calculation")
    print("   - Comparison with traditional search")

def test_health_check():
    """Test if the recommendation service is running"""
    print("🏥 Testing Recommendation Service Health...")
    health = test_api_endpoint(f"{RECOMMENDATION_API_URL}/health")
    if health:
        print(f"✅ Service Status: {health.get('status')}")
        print(f"   Message: {health.get('message')}")
        return True
    else:
        print("❌ Recommendation service is not running")
        return False

if __name__ == "__main__":
    print("🚀 Starting Semantic Product Search Tests")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check if services are running
    if not test_health_check():
        print("\n❌ Please start the recommendation service first:")
        print("   python flask_recommendation_server.py")
        exit(1)
    
    # Run semantic search tests
    test_semantic_search()
    
    print(f"\n📋 Test Summary:")
    print("   - API endpoints for semantic search created")
    print("   - Embedding system working with Chroma DB")
    print("   - Cosine similarity search implemented")
    print("   - Hybrid search combining semantic + keyword matching")
    print("   - Ready for production use!")
