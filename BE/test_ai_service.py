"""
Test script for AI Service functionality
Run this script to test the semantic search capabilities
"""

import asyncio
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ai_service import AIService

async def test_ai_service():
    """Test the AI service functionality"""
    
    print("🤖 Testing AI Service...")
    print("=" * 50)
    
    # Initialize AI service
    ai_service = AIService()
    
    # Test 1: Check collection stats
    print("\n1. Testing ChromaDB connection...")
    stats = ai_service.get_collection_stats()
    print(f"Collection stats: {stats}")
    
    # Test 2: Embed all products
    print("\n2. Embedding all products...")
    result = await ai_service.embed_all_products()
    print(f"Embedding result: {result}")
    
    if result["status"] != "success":
        print("❌ Failed to embed products. Please check your setup.")
        return
    
    # Test 3: Test search intent extraction
    print("\n3. Testing search intent extraction...")
    test_queries = [
        "I want a cheap laptop",
        "Show me furniture under $500",
        "I need a good quality refrigerator",
        "Find me electronics with high ratings"
    ]
    
    for query in test_queries:
        intent = ai_service.extract_search_intent(query)
        print(f"Query: '{query}'")
        print(f"Intent: {intent}")
        print()
    
    # Test 4: Test semantic search
    print("\n4. Testing semantic search...")
    search_queries = [
        "laptop computer",
        "comfortable chair",
        "kitchen appliance",
        "gaming equipment"
    ]
    
    for query in search_queries:
        print(f"\nSearching for: '{query}'")
        result = await ai_service.semantic_search(query, limit=3)
        
        if result["status"] == "success":
            print(f"Found {result['total_results']} products:")
            for product in result["products"]:
                print(f"  - {product['name']} ({product['category']}) - ${product['price']} - Similarity: {product['similarity_score']:.3f}")
        else:
            print(f"Search failed: {result['message']}")
    
    print("\n✅ AI Service testing completed!")

if __name__ == "__main__":
    asyncio.run(test_ai_service())
