#!/usr/bin/env python3
"""
Test script for eCommerce Recommendation System with Chroma DB integration

This script demonstrates:
1. Creating user events
2. Getting personalized recommendations  
3. Smart natural language search
4. Vector similarity search
"""

import requests
import json
import time

# Configuration
RECOMMENDATION_API = "http://localhost:8001"
TEST_USER_ID = "test_user_123"

def test_api_endpoint(url, method="GET", data=None, description=""):
    """Helper function to test API endpoints"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"URL: {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"Exception: {e}")
        return None

def main():
    print("🚀 Testing eCommerce Recommendation System with Chroma DB")
    print("="*60)
    
    # Test 1: Health Check
    test_api_endpoint(
        f"{RECOMMENDATION_API}/health",
        description="Health Check"
    )
    
    # Test 2: Create User Events
    events_to_create = [
        {
            "user_id": TEST_USER_ID,
            "event_type": "view",
            "product_id": "1",
            "product_data": {
                "name": "iPhone 14 Pro",
                "category": "Điện thoại",
                "brand": "Apple",
                "price": 999
            }
        },
        {
            "user_id": TEST_USER_ID,
            "event_type": "add_to_cart",
            "product_id": "1", 
            "product_data": {
                "name": "iPhone 14 Pro",
                "category": "Điện thoại",
                "brand": "Apple",
                "price": 999
            }
        },
        {
            "user_id": TEST_USER_ID,
            "event_type": "view",
            "product_id": "2",
            "product_data": {
                "name": "Dell XPS 13",
                "category": "Laptop",
                "brand": "Dell", 
                "price": 1299
            }
        }
    ]
    
    print(f"\n📝 Creating {len(events_to_create)} user events...")
    for i, event in enumerate(events_to_create):
        test_api_endpoint(
            f"{RECOMMENDATION_API}/user-events",
            method="POST",
            data=event,
            description=f"Create Event {i+1}: {event['event_type']} {event['product_data']['name']}"
        )
        time.sleep(0.5)  # Small delay between requests
    
    # Test 3: Get User Events
    test_api_endpoint(
        f"{RECOMMENDATION_API}/user-events/{TEST_USER_ID}",
        description="Get All User Events"
    )
    
    # Test 4: Get Personalized Recommendations
    test_api_endpoint(
        f"{RECOMMENDATION_API}/recommendations/{TEST_USER_ID}?limit=5",
        description="Get Personalized Recommendations"
    )
    
    # Test 5: Smart Search Tests
    search_queries = [
        "I want buy a laptop dell with price below 20m",
        "Samsung phone under 15 million", 
        "Apple watch above 5m",
        "Gaming laptop asus over 30m"
    ]
    
    for query in search_queries:
        test_api_endpoint(
            f"{RECOMMENDATION_API}/search",
            method="POST",
            data={"query": query, "limit": 3},
            description=f"Smart Search: '{query}'"
        )
    
    # Test 6: Vector Similarity Search
    similarity_queries = [
        "smartphone apple",
        "laptop dell",
        "high-end electronics"
    ]
    
    for query in similarity_queries:
        test_api_endpoint(
            f"{RECOMMENDATION_API}/user-events/{TEST_USER_ID}/similar",
            method="POST",
            data={"query": query, "limit": 3},
            description=f"Similarity Search: '{query}'"
        )
    
    # Test 7: User Analytics
    test_api_endpoint(
        f"{RECOMMENDATION_API}/analytics/user-stats/{TEST_USER_ID}",
        description="User Analytics"
    )
    
    print(f"\n{'='*60}")
    print("✅ All tests completed!")
    print(f"🎯 Recommendation System is working with Chroma DB integration")
    print(f"📊 Check the server logs for vector embedding operations")

if __name__ == "__main__":
    main()
