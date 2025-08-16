#!/usr/bin/env python3
"""
Test BE API cho semantic search
"""

import requests
import json

def test_be_semantic_api():
    """Test các API semantic search mới ở BE"""
    
    print("🔍 Testing BE Semantic Search APIs")
    print("=" * 50)
    
    # Test 1: Semantic Search
    print("\n1. Testing /search/semantic")
    semantic_data = {
        "query": "iPhone Apple smartphone",
        "limit": 5,
        "min_similarity": 0.2
    }
    
    response = requests.post('http://localhost:8001/search/semantic', json=semantic_data)
    
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Semantic Search successful:")
        print(f"   Query: {results['query']}")
        print(f"   Search Type: {results['search_type']}")
        print(f"   Results: {results['total_found']}")
        
        for i, product in enumerate(results['results'][:3], 1):
            print(f"   {i}. {product['name']} (Similarity: {product.get('similarity_score', 'N/A')})")
    else:
        print(f"❌ Semantic search failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test 2: Hybrid Search
    print("\n2. Testing /search/hybrid")
    hybrid_data = {
        "query": "gaming laptop powerful",
        "limit": 5,
        "semantic_weight": 0.7
    }
    
    response = requests.post('http://localhost:8001/search/hybrid', json=hybrid_data)
    
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Hybrid Search successful:")
        print(f"   Query: {results['query']}")
        print(f"   Search Type: {results['search_type']}")
        print(f"   Results: {results['total_found']}")
        print(f"   Semantic Weight: {results['semantic_weight']}")
        
        for i, product in enumerate(results['results'][:3], 1):
            hybrid_score = product.get('hybrid_score', 'N/A')
            semantic_score = product.get('semantic_score', 'N/A')
            keyword_score = product.get('keyword_score', 'N/A')
            print(f"   {i}. {product['name']}")
            print(f"      Hybrid: {hybrid_score}, Semantic: {semantic_score}, Keyword: {keyword_score}")
    else:
        print(f"❌ Hybrid search failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test 3: So sánh với Smart Search hiện tại
    print("\n3. Comparing with existing /search/smart")
    smart_data = {
        "query": "iPhone Apple smartphone",
        "limit": 5
    }
    
    response = requests.post('http://localhost:8001/search/smart', json=smart_data)
    
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Smart Search comparison:")
        print(f"   Query: {results['query']}")
        print(f"   Search Type: {results['search_type']}")
        print(f"   Results: {results['total_found']}")
        
        for i, product in enumerate(results['results'][:3], 1):
            print(f"   {i}. {product['name']} - {product.get('category', 'N/A')}")
    else:
        print(f"❌ Smart search failed: {response.status_code}")
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    test_be_semantic_api()
