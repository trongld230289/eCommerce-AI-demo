#!/usr/bin/env python3
"""
Product Embedding Script
========================

This script calls the FastAPI endpoint to embed all products into ChromaDB.
It requires the FastAPI server to be running and an OpenAI API key to be configured.

Usage:
    python embed_products.py
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# API Configuration
BASE_URL = "http://localhost:8000"
EMBED_ENDPOINT = "/ai/embed-products"

class ProductEmbedder:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=300.0)  # 5 minute timeout
    
    async def check_server_health(self) -> bool:
        """Check if the FastAPI server is running"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ FastAPI server is running")
                return True
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            print("Make sure the FastAPI server is running on http://localhost:8000")
            return False
    
    async def embed_products(self) -> Dict[str, Any]:
        """Call the embed products API endpoint"""
        try:
            print("🔄 Starting product embedding process...")
            print("📡 Calling API endpoint: POST /ai/embed-products")
            
            response = await self.client.post(f"{self.base_url}{EMBED_ENDPOINT}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Products embedded successfully!")
                print(f"📊 Results: {json.dumps(result, indent=2)}")
                return result
            else:
                print(f"❌ API call failed with status: {response.status_code}")
                print(f"📄 Response: {response.text}")
                return {"status": "error", "message": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            print(f"❌ Error calling embedding API: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the ChromaDB collection"""
        try:
            response = await self.client.get(f"{self.base_url}/ai/collection-info")
            if response.status_code == 200:
                result = response.json()
                print("📊 Collection Info:")
                print(f"   • Total documents: {result.get('count', 'unknown')}")
                print(f"   • Collection name: {result.get('name', 'unknown')}")
                return result
            else:
                print(f"⚠️  Could not get collection info: {response.status_code}")
                return {}
        except Exception as e:
            print(f"⚠️  Error getting collection info: {e}")
            return {}
    
    async def test_search(self, query: str = "camera") -> Dict[str, Any]:
        """Test semantic search after embedding"""
        try:
            print(f"🔍 Testing search with query: '{query}'")
            response = await self.client.post(
                f"{self.base_url}/ai/search",
                json={"user_input": query, "limit": 3}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Search test successful!")
                print(f"📄 Found {len(result.get('products', []))} products")
                return result
            else:
                print(f"⚠️  Search test failed: {response.status_code}")
                return {}
        except Exception as e:
            print(f"⚠️  Error testing search: {e}")
            return {}
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

async def main():
    """Main function to run the embedding process"""
    print("""
🤖 Product Embedding Tool
=========================
This tool will embed all products from Firebase into ChromaDB for semantic search.

Requirements:
• FastAPI server running on http://localhost:8000
• OpenAI API key configured in environment
• Firebase products data available

Starting process...
""")
    
    embedder = ProductEmbedder()
    
    try:
        # Step 1: Check server health
        if not await embedder.check_server_health():
            return
        
        # Step 2: Get current collection info (before embedding)
        print("\n📊 Current ChromaDB collection status:")
        await embedder.get_collection_info()
        
        # Step 3: Embed products
        print("\n🚀 Starting embedding process...")
        result = await embedder.embed_products()
        
        if result.get("status") == "success":
            print(f"\n🎉 Embedding completed successfully!")
            print(f"📈 Total products embedded: {result.get('total_products', 'unknown')}")
            
            # Step 4: Get updated collection info
            print("\n📊 Updated ChromaDB collection status:")
            await embedder.get_collection_info()
            
            # Step 5: Test search functionality
            print("\n🔍 Testing search functionality...")
            await embedder.test_search("camera")
            
            print("\n✅ All done! You can now use semantic search in your application.")
            
        else:
            print(f"\n❌ Embedding failed: {result.get('message', 'Unknown error')}")
            
    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        await embedder.close()

if __name__ == "__main__":
    asyncio.run(main())
