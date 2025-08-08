# eCommerce Recommendation API

A FastAPI backend service that provides product recommendations and AI-powered chatbot functionality for an eCommerce application.

## Features

- **Personalized Recommendations**: Returns products based on user preferences when `userId` is provided
- **Default Recommendations**: Returns popular products when `userId` is null or not found
- **AI-Powered Chatbot**: Uses OpenAI function calling to parse user queries and search products
- **Product Search**: Advanced filtering by category, brand, price range, and keywords
- **CORS Support**: Configured for frontend integration
- **Product Management**: Full CRUD operations for products

## API Endpoints

### GET /recommendations
Get product recommendations for a user.

**Query Parameters:**
- `user_id` (optional): User ID for personalized recommendations
- `limit` (optional, default=10): Number of recommendations to return (1-50)

**Example Requests:**
```bash
# Get default recommendations
curl "http://localhost:8000/recommendations"

# Get personalized recommendations for a user
curl "http://localhost:8000/recommendations?user_id=user1&limit=5"
```

### POST /chatbot
Process chatbot queries using OpenAI function calling to extract product search parameters.

**Request Body:**
```json
{
  "message": "I want to find a Samsung phone under $2000",
  "user_id": "user1"
}
```

**Response:**
```json
{
  "response": "I found 3 products matching your criteria:\n\n• Samsung Galaxy S24 Ultra...",
  "products": [...],
  "search_params": {
    "category": "Điện thoại",
    "brand": "Samsung",
    "max_price": 50000000
  }
}
```

### GET /search
Direct product search endpoint.

**Query Parameters:**
- `category` (optional): Product category
- `brand` (optional): Product brand  
- `min_price` (optional): Minimum price
- `max_price` (optional): Maximum price
- `keywords` (optional): Keywords (comma-separated)

**Example:**
```bash
curl "http://localhost:8000/search?brand=Samsung&category=Điện thoại&max_price=50000000"
```

### GET /products
Get all available products.

### GET /products/{product_id}
Get a specific product by ID.

## Installation

1. Navigate to the mock-backend directory:
```bash
cd mock-backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up OpenAI API for chatbot functionality:
```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_actual_api_key_here
```

**Note**: If no OpenAI API key is provided, the chatbot will use a fallback keyword matching system.

4. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## User Preferences

The system includes mock user preferences for testing personalized recommendations:

- `user1`: Prefers phones and laptops from Apple and Samsung
- `user2`: Prefers headphones and cameras from Sony and Canon  
- `user3`: Prefers gaming devices and TVs from Nintendo and LG
- `testuser`: Prefers laptops and headphones from Apple and Sony

## Recommendation Logic

1. **With User ID**: 
   - Filters products by user's preferred categories and brands
   - Falls back to popular products if not enough matches
   - Shuffles results for variety

2. **Without User ID**:
   - Returns products sorted by rating and review count
   - Provides consistent popular products
