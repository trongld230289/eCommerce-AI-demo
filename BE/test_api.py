#!/usr/bin/env python3
"""
Simple script to test the API endpoints
"""

import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing eCommerce API")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test get all products
    print("\n2. Testing get all products...")
    try:
        response = requests.get(f"{base_url}/products")
        print(f"   Status Code: {response.status_code}")
        products = response.json()
        print(f"   Number of products: {len(products)}")
        if products:
            print(f"   First product ID: {products[0].get('id')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test get product by ID = 1
    print("\n3. Testing get product by ID = 1...")
    try:
        response = requests.get(f"{base_url}/products/1")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            product = response.json()
            print(f"   Product found:")
            print(f"   - ID: {product.get('id')}")
            print(f"   - Name: {product.get('name')}")
            print(f"   - Price: ${product.get('price')}")
            print(f"   - Category: {product.get('category')}")
            print(f"   - Brand: {product.get('brand')}")
            print(f"   - Description: {product.get('description')}")
            print(f"   - Stock: {product.get('stock')}")
            print(f"   - Weekly Views: {product.get('weeklyViews')}")
        else:
            print(f"   Error response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test other product IDs
    print("\n4. Testing other product IDs...")
    for product_id in [2, 3, 4, 5]:
        try:
            response = requests.get(f"{base_url}/products/{product_id}")
            if response.status_code == 200:
                product = response.json()
                print(f"   Product {product_id}: {product.get('name')} - ${product.get('price')}")
            else:
                print(f"   Product {product_id}: Not found")
        except Exception as e:
            print(f"   Product {product_id}: Error - {e}")

if __name__ == "__main__":
    test_api()
