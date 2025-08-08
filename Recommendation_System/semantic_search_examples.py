#!/usr/bin/env python3
"""
Semantic Product Search API Usage Examples
This file shows how to use the new semantic search functionality
"""

import requests
import json

# API Configuration
API_BASE_URL = "http://localhost:8001"

def semantic_search_example():
    """Example of using semantic search API"""
    
    # 1. Check if embeddings are ready
    status_response = requests.get(f"{API_BASE_URL}/search/status")
    status = status_response.json()
    
    print("🔍 Semantic Search Status:")
    print(f"   Embeddings Ready: {status['embeddings_initialized']}")
    print(f"   Products in Cache: {status['products_in_cache']}")
    
    # 2. If embeddings not ready, initialize them
    if not status['embeddings_initialized']:
        print("\n📚 Initializing product embeddings...")
        embed_response = requests.post(f"{API_BASE_URL}/products/embed")
        if embed_response.status_code == 200:
            print("✅ Embeddings initialized successfully")
        else:
            print("❌ Failed to initialize embeddings")
            return
    
    # 3. Perform semantic search
    search_queries = [
        "điện thoại camera đẹp",
        "laptop gaming mạnh",
        "tai nghe bluetooth",
        "smartphone cao cấp"
    ]
    
    for query in search_queries:
        print(f"\n🔍 Searching for: '{query}'")
        
        # Semantic search request
        search_data = {
            "query": query,
            "limit": 5,
            "min_similarity": 0.3
        }
        
        response = requests.post(f"{API_BASE_URL}/search/semantic", json=search_data)
        
        if response.status_code == 200:
            results = response.json()
            print(f"   Found {results['count']} products:")
            
            for i, result in enumerate(results['results'], 1):
                product = result['product_data']
                similarity = result['similarity_score']
                print(f"   {i}. {product['name']} (Similarity: {similarity:.3f})")
                print(f"      Price: {product['price']:,.0f} VND | Category: {product['category']}")
        else:
            print(f"   ❌ Search failed: {response.text}")

def hybrid_search_example():
    """Example of using hybrid search API"""
    
    query = "iPhone 14 Pro camera"
    
    print(f"\n🔀 Hybrid Search for: '{query}'")
    
    # Hybrid search request
    search_data = {
        "query": query,
        "limit": 5,
        "semantic_weight": 0.7  # 70% semantic, 30% keyword matching
    }
    
    response = requests.post(f"{API_BASE_URL}/search/hybrid", json=search_data)
    
    if response.status_code == 200:
        results = response.json()
        print(f"   Found {results['count']} products:")
        
        for i, result in enumerate(results['results'], 1):
            product = result['product_data']
            hybrid_score = result['hybrid_score']
            semantic_score = result['semantic_score']
            keyword_score = result['keyword_score']
            
            print(f"   {i}. {product['name']}")
            print(f"      Hybrid Score: {hybrid_score:.3f} (Semantic: {semantic_score:.3f}, Keyword: {keyword_score:.3f})")
            print(f"      Price: {product['price']:,.0f} VND")
    else:
        print(f"   ❌ Search failed: {response.text}")

if __name__ == "__main__":
    print("🚀 Semantic Product Search API Examples")
    print("=" * 50)
    
    # Test semantic search
    semantic_search_example()
    
    # Test hybrid search
    hybrid_search_example()
    
    print("\n✅ Examples completed!")
    print("\n📋 Available API Endpoints:")
    print("   POST /search/semantic - Pure semantic search with embeddings")
    print("   POST /search/hybrid - Hybrid semantic + keyword search")
    print("   POST /products/embed - Initialize/refresh product embeddings")
    print("   GET /search/status - Check search system status")
