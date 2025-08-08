# eCommerce Recommendation System with Chroma DB

A Flask-based recommendation system that provides personalized product recommendations and smart search capabilities using **Chroma DB vector storage** for user behavior analysis.

## Features

- **Vector-Based Event Storage**: Store user interactions in Chroma DB with automatic embeddings
- **User Event Tracking**: CRUD operations for user interactions (views, clicks, purchases)
- **Personalized Recommendations**: Get top 5 product recommendations based on user behavior patterns
- **Smart NLP Search**: Natural language search with intelligent query parsing (support multiple languages)
- **Similarity Search**: Find similar user events using vector similarity
- **Analytics**: User behavior analytics and insights
- **Fallback Storage**: Automatic fallback to in-memory storage when Chroma DB unavailable

## Tech Stack

- **Flask**: Web framework
- **Chroma DB**: Vector database for embeddings and similarity search
- **Natural Language Processing**: Query parsing and text analysis
- **RESTful APIs**: Complete CRUD operations

## API Endpoints

### Health Check
```
GET /health
```

### User Events (CRUD)

#### Create User Event
```
POST /user-events
Content-Type: application/json

{
  "user_id": "user123",
  "event_type": "view",        // view, click, add_to_cart, purchase
  "product_id": "1", 
  "product_data": {            // Optional product details
    "name": "iPhone 14",
    "category": "Điện thoại",
    "brand": "Apple",
    "price": 999
  },
  "metadata": {}               // Optional additional data
}
```

#### Get User Events
```
GET /user-events/{user_id}?limit=100&event_type=view
```

#### Delete Specific Event
```
DELETE /user-events/{user_id}/{event_id}
```

#### Delete All User Events
```
DELETE /user-events/{user_id}
```

#### Find Similar Events (Vector Search)
```
POST /user-events/{user_id}/similar
Content-Type: application/json

{
  "query": "smartphone apple",
  "limit": 10
}

Response:
{
  "user_id": "user123",
  "query": "smartphone apple",
  "similar_events": [
    {
      "id": "event_id",
      "event_type": "view",
      "product_id": "1",
      "similarity_score": 0.95,
      "product_data": {...}
    }
  ],
  "count": 5
}
```

### Recommendations

#### Get User Recommendations
```
GET /recommendations/{user_id}?limit=5

Response:
{
  "user_id": "user123",
  "recommendations": [...],     // Top 5 recommended products
  "count": 5,
  "timestamp": "2025-08-08T..."
}
```

### Smart Search

#### Natural Language Search
```
POST /search
Content-Type: application/json

{
  "query": "I want buy a laptop dell with price below 20m",
  "limit": 10
}

Response:
{
  "query": "I want buy a laptop dell with price below 20m",
  "parsed_filters": {
    "brand": "Dell",
    "category": "Laptop", 
    "max_price": 20000000,
    "keywords": "laptop"
  },
  "results": [...],            // Filtered products
  "count": 5,
  "total_found": 8
}
```

#### Search Query Examples:
- "I want buy a laptop dell with price below 20m"
- "Samsung phone under 15 million"
- "Apple watch above 5m"
- "Headphones sony less than 2m"
- "Gaming laptop asus over 30m"

### Analytics

#### User Analytics
```
GET /analytics/user-stats/{user_id}

Response:
{
  "user_id": "user123",
  "total_events": 25,
  "event_types": {
    "view": 15,
    "add_to_cart": 8,
    "purchase": 2
  },
  "top_categories": {
    "Điện thoại": 10,
    "Laptop": 8
  },
  "top_brands": {
    "Apple": 12,
    "Dell": 6
  }
}
```

### Test Endpoints

#### Create Sample Events (for testing)
```
POST /test/sample-events
```

## How It Works

### 1. Chroma DB Vector Storage
- **Automatic Embeddings**: User events are converted to vector embeddings for similarity search
- **Persistent Storage**: Events stored in local Chroma DB with metadata indexing
- **Vector Similarity**: Find related user behaviors using cosine similarity
- **Fallback System**: Automatic fallback to in-memory storage if Chroma DB unavailable

### 2. User Event Tracking
- BE calls `/user-events` to record user interactions
- Events include: product views, clicks, add to cart, purchases
- Each event stores user ID, product details, timestamp, and vector embeddings
- Supports real-time similarity search across user behaviors

### 3. Recommendation Algorithm
- **Behavior Analysis**: Analyzes user's past events using vector similarity
- **Preference Extraction**: Identifies preferred categories, brands, price ranges
- **Collaborative Patterns**: Finds users with similar behavior patterns
- **Scoring System**: Scores products based on user history, similarity, and product ratings
- **Returns**: Top 5 most relevant products with confidence scores

### 4. Smart Search Parser
- **Multi-language Support**: English + Vietnamese natural language processing
- **Brand Recognition**: Extracts brand names (Apple, Samsung, Dell, HP, etc.)
- **Category Detection**: Identifies product categories (laptop, phone, tablet, etc.)
- **Price Parsing**: Handles price constraints (below 20m, under 15k, above 10m)
- **Contextual Understanding**: Processes complex queries with multiple filters

### 5. Vector Similarity Search
- **Semantic Search**: Find similar products and user behaviors
- **Embedding-based**: Uses pre-trained models for text understanding
- **Real-time**: Fast similarity search with Chroma DB indexing
- **Configurable**: Adjustable similarity thresholds and result limits

### 4. Integration with BE
The BE system calls this recommendation API to:
```python
# In BE flask_server.py
def track_user_event(user_id, event_type, product_data):
    try:
        response = requests.post('http://localhost:8001/user-events', json={
            'user_id': user_id,
            'event_type': event_type,
            'product_id': str(product_data['id']),
            'product_data': product_data
        })
        return response.status_code == 201
    except:
        return False
```

## Installation & Setup

1. **Install Dependencies:**
```bash
cd Recommendation_System
pip install -r requirements.txt
```

2. **Start the Service:**
```bash
python flask_recommendation_server.py
```

3. **Service will run on:**
```
http://localhost:8001
```

## Configuration

- **Port**: 8001 (configurable via `CHROMA_PORT`)
- **BE API URL**: http://localhost:8000 (configurable via `BE_API_URL`)
- **Cache Duration**: 5 minutes for product data

## Future Enhancements

- **Chroma DB Integration**: Replace in-memory storage with vector database
- **Advanced ML Models**: Implement collaborative filtering and deep learning
- **Real-time Updates**: WebSocket support for live recommendations
- **A/B Testing**: Multiple recommendation algorithms
- **Performance Optimization**: Redis caching, async processing
