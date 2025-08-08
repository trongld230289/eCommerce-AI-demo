import requests

# Test semantic search with different queries
queries = [
    "iPhone Apple smartphone",
    "gaming laptop powerful",
    "bluetooth headphones",
    "camera photography",
    "Dell XPS laptop"
]

print("🔍 Testing Semantic Search with Various Queries")
print("=" * 50)

for query in queries:
    print(f"\n🔍 Query: '{query}'")
    
    response = requests.post('http://localhost:8001/search/semantic', 
                           json={'query': query, 'limit': 5, 'min_similarity': 0.1})
    
    if response.status_code == 200:
        results = response.json()
        print(f"   Found {results['count']} products:")
        
        for i, result in enumerate(results['results'], 1):
            product = result['product_data']
            score = result['similarity_score']
            print(f"   {i}. {product['name']} (Score: {score:.3f})")
            print(f"      Category: {product['category']} | Brand: {product['brand']}")
    else:
        print(f"   Error: {response.text}")

print("\n🔀 Testing Hybrid Search")
print("-" * 30)

hybrid_query = "iPhone camera quality"
print(f"\n🔍 Hybrid Query: '{hybrid_query}'")

response = requests.post('http://localhost:8001/search/hybrid', 
                       json={'query': hybrid_query, 'limit': 5, 'semantic_weight': 0.7})

if response.status_code == 200:
    results = response.json()
    print(f"   Found {results['count']} products:")
    
    for i, result in enumerate(results['results'], 1):
        product = result['product_data']
        hybrid_score = result['hybrid_score']
        semantic_score = result['semantic_score']
        keyword_score = result['keyword_score']
        print(f"   {i}. {product['name']}")
        print(f"      Hybrid: {hybrid_score:.3f} (Semantic: {semantic_score:.3f}, Keyword: {keyword_score:.3f})")
else:
    print(f"   Error: {response.text}")
