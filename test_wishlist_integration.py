#!/usr/bin/env python3
"""
Test script to verify wishlist API integration
"""

import requests
import json
import sys

def test_wishlist_api():
    """Test the wishlist API endpoints"""
    base_url = "http://localhost:8000"
    
    # Test endpoints
    print("🧪 Testing Wishlist API Integration")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing API health...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ API is running")
            print(f"   Response: {response.json()}")
        else:
            print("❌ API health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the backend is running on localhost:8000")
        return False
    
    # Test 2: Test with demo token
    print("\n2. Testing authentication with demo token...")
    headers = {
        "Authorization": "Bearer demo-token",
        "Content-Type": "application/json"
    }
    
    try:
        # Test auth verification
        response = requests.post(f"{base_url}/api/auth/verify", headers=headers)
        if response.status_code == 200:
            print("✅ Demo token authentication works")
            user_data = response.json()
            print(f"   User: {user_data}")
        else:
            print(f"❌ Auth verification failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Auth test error: {e}")
        return False
    
    # Test 3: Test wishlist endpoints
    print("\n3. Testing wishlist endpoints...")
    
    # Get user wishlists (should be empty initially)
    try:
        response = requests.get(f"{base_url}/api/wishlist", headers=headers)
        if response.status_code == 200:
            wishlists = response.json()
            print(f"✅ Get wishlists: {len(wishlists)} wishlists found")
            print(f"   Wishlists: {wishlists}")
        else:
            print(f"❌ Get wishlists failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get wishlists error: {e}")
        return False
    
    # Create a new wishlist
    try:
        create_data = {"name": "Test Wishlist"}
        response = requests.post(f"{base_url}/api/wishlist", 
                               headers=headers, 
                               json=create_data)
        if response.status_code == 200:
            wishlist = response.json()
            print("✅ Create wishlist successful")
            print(f"   Created: {wishlist}")
            wishlist_id = wishlist.get('id')
        else:
            print(f"❌ Create wishlist failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Create wishlist error: {e}")
        return False
    
    # Add product to wishlist (using product ID 1)
    if wishlist_id:
        try:
            add_product_data = {"product_id": 1}
            response = requests.post(f"{base_url}/api/wishlist/{wishlist_id}/products", 
                                   headers=headers, 
                                   json=add_product_data)
            if response.status_code == 200:
                updated_wishlist = response.json()
                print("✅ Add product to wishlist successful")
                print(f"   Updated wishlist: {updated_wishlist}")
            else:
                print(f"❌ Add product failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Add product error: {e}")
    
    print("\n🎉 Wishlist API integration test completed!")
    print("\nNext steps:")
    print("1. Start the frontend: cd FE && npm start")
    print("2. Login with any email/password in the frontend")
    print("3. Try adding products to wishlist")
    print("4. Check if data persists in the database")
    
    return True

if __name__ == "__main__":
    success = test_wishlist_api()
    sys.exit(0 if success else 1)
