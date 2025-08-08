# Semantic Product Search API - Documentation

## Overview

This document describes the newly implemented Semantic Product Search API that uses text embeddings and cosine similarity for intelligent product search. The system leverages Chroma DB for vector storage and retrieval.

## Features

### 🧠 Semantic Search
- **Text Embeddings**: Products are converted to vector embeddings using their name, category, brand, description, and tags
- **Cosine Similarity**: Search queries are matched against product embeddings using cosine similarity
- **Intelligent Matching**: Finds semantically similar products even when exact keywords don't match

### 🔀 Hybrid Search
- **Combined Approach**: Merges semantic search with traditional keyword matching
- **Weighted Results**: Configurable balance between semantic and keyword matching (default 70% semantic, 30% keyword)
- **Better Coverage**: Ensures both semantic understanding and exact keyword matches

### 💾 Vector Storage
- **Chroma DB Integration**: Persistent vector storage with automatic embedding generation
- **Product Metadata**: Stores product information alongside embeddings for efficient retrieval
- **Auto-initialization**: Automatically embeds products when first accessed

## API Endpoints

### 1. Semantic Search
```http
POST /search/semantic
Content-Type: application/json

{
  "query": "iPhone camera quality",
  "limit": 10,
  "min_similarity": 0.3
}
```

**Response:**
```json
{
  "query": "iPhone camera quality",
  "search_type": "semantic",
  "results": [
    {
      "product_id": "1",
      "similarity_score": 0.856,
      "product_data": {
        "id": 1,
        "name": "iPhone 15 Pro",
        "category": "Smartphones",
        "brand": "Apple",
        "price": 999.99,
        "rating": 4.8
      },
      "matched_text": "iphone 15 pro smartphones apple...",
      "metadata": {...}
    }
  ],
  "count": 1,
  "min_similarity": 0.3,
  "timestamp": "2025-08-09T00:35:00"
}
```

### 2. Hybrid Search
```http
POST /search/hybrid
Content-Type: application/json

{
  "query": "gaming laptop powerful",
  "limit": 5,
  "semantic_weight": 0.7
}
```

**Response:**
```json
{
  "query": "gaming laptop powerful",
  "search_type": "hybrid",
  "results": [
    {
      "product_id": "5",
      "hybrid_score": 0.782,
      "semantic_score": 0.654,
      "keyword_score": 0.890,
      "product_data": {...}
    }
  ],
  "count": 1,
  "semantic_weight": 0.7,
  "timestamp": "2025-08-09T00:35:00"
}
```

### 3. Initialize Embeddings
```http
POST /products/embed
Content-Type: application/json

{
  "force_refresh": true
}
```

**Response:**
```json
{
  "message": "Products embedded successfully",
  "total_products": 18,
  "status": "success",
  "timestamp": "2025-08-09T00:35:00"
}
```

### 4. Search System Status
```http
GET /search/status
```

**Response:**
```json
{
  "chroma_available": true,
  "embeddings_initialized": true,
  "products_in_cache": 18,
  "collection_available": true,
  "timestamp": "2025-08-09T00:35:00"
}
```

## Product Embedding Process

### 1. Text Generation
For each product, a comprehensive text representation is created:
```
"iPhone 15 Pro Smartphones Apple Latest iPhone with A17 Pro chip smartphone apple ios budget affordable"
```

### 2. Metadata Storage
Key product information is stored as metadata:
```json
{
  "product_id": "1",
  "name": "iPhone 15 Pro",
  "category": "Smartphones", 
  "brand": "Apple",
  "price": 999.99,
  "rating": 4.8,
  "featured": true
}
```

### 3. Vector Storage
- Text embeddings generated automatically by Chroma DB
- Stored in `product_embeddings` collection
- Indexed for fast similarity search

## Usage Examples

### Basic Semantic Search
```python
import requests

# Search for products semantically
response = requests.post('http://localhost:8001/search/semantic', json={
    'query': 'laptop for gaming',
    'limit': 5,
    'min_similarity': 0.3
})

results = response.json()
for result in results['results']:
    product = result['product_data']
    score = result['similarity_score']
    print(f"{product['name']} (Score: {score:.3f})")
```

### Hybrid Search with Custom Weights
```python
# 80% semantic, 20% keyword matching
response = requests.post('http://localhost:8001/search/hybrid', json={
    'query': 'iPhone camera',
    'limit': 5,
    'semantic_weight': 0.8
})
```

### Initialize Embeddings
```python
# Force refresh all product embeddings
response = requests.post('http://localhost:8001/products/embed', json={
    'force_refresh': True
})
```

## Performance Features

### Caching
- **Product Cache**: Products cached for 5 minutes to reduce API calls
- **Embedding Cache**: Vector embeddings persisted in Chroma DB
- **Automatic Refresh**: Cache updated when products change

### Similarity Thresholds
- **Minimum Similarity**: Filter out low-relevance results (default 0.3)
- **Scoring**: Cosine similarity scores from 0.0 to 1.0
- **Ranking**: Results sorted by similarity score

### Fallback Support
- **Graceful Degradation**: Falls back to keyword search if embeddings fail
- **Error Handling**: Comprehensive error handling and logging
- **Status Monitoring**: Real-time status checking

## Comparison with Traditional Search

### Traditional Smart Search
- **Keyword Matching**: Exact word matches in product text
- **Filter-based**: Category, brand, price range filters
- **Rule-based**: Predefined patterns and regex matching

### Semantic Search
- **Intent Understanding**: Understands search intent beyond keywords
- **Contextual Matching**: Finds related products even with different terms
- **Vector Similarity**: Mathematical similarity calculation

### Example Comparison
**Query**: "smartphone camera chất lượng cao"

**Traditional Results**: Limited matches based on exact keywords
**Semantic Results**: iPhones, Samsung Galaxy, camera phones based on meaning
**Hybrid Results**: Best of both approaches with balanced scoring

## Technical Implementation

### Technologies Used
- **Chroma DB**: Vector database for embeddings
- **Flask**: Web API framework
- **Cosine Similarity**: Vector similarity calculation
- **Automatic Embeddings**: Built-in text embedding generation

### Architecture
```
[Frontend] -> [Recommendation API] -> [Chroma DB]
                     ↓
[Product Cache] -> [Backend API] -> [Product Database]
```

### Data Flow
1. **Product Sync**: Products fetched from backend API
2. **Text Processing**: Product text generated for embedding
3. **Vector Generation**: Chroma DB creates embeddings automatically
4. **Storage**: Vectors stored with metadata in collection
5. **Search**: Query embedded and compared using cosine similarity
6. **Results**: Ranked results returned with similarity scores

## Testing and Validation

### Test Queries Verified
✅ "iPhone Apple smartphone" → iPhone 15 Pro (Score: 0.319)
✅ "gaming laptop powerful" → Gaming Laptop (Score: 0.343)  
✅ "bluetooth headphones" → Wireless Headphones (Score: 0.305)
✅ "Dell XPS laptop" → Dell XPS 13 (Score: 0.365)

### API Status
✅ All endpoints functional
✅ Error handling implemented
✅ Logging and monitoring active
✅ Vector storage operational
✅ 18 products successfully embedded

## Next Steps & Recommendations

### Enhancements
1. **Multilingual Support**: Better Vietnamese text handling
2. **Custom Embeddings**: Fine-tuned models for product search
3. **User Personalization**: Include user preferences in scoring
4. **Analytics**: Track search patterns and improve relevance

### Production Considerations
1. **Embedding Model**: Consider OpenAI or Azure OpenAI for better embeddings
2. **Performance**: Implement proper caching and indexing
3. **Monitoring**: Add detailed metrics and alerting
4. **Scaling**: Horizontal scaling for high traffic

---

**Status**: ✅ Fully Implemented and Tested
**Last Updated**: August 9, 2025
**API Version**: 1.0.0
