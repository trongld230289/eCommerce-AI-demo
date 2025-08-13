# eCommerce Backend API (FastAPI)

A modern, high-performance backend API built with FastAPI for the eCommerce application.

## 🚀 Quick Start

### Option 1: Convenient Startup (Recommended)
```bash
python run_BE.py
```

### Option 2: Direct Server Launch
```bash
# Main FastAPI server
python main.py

# Alternative FastAPI server
python fastapi_server.py

# Simple startup
python start_simple.py
```

### Option 3: Using Uvicorn
```bash
# Main server
uvicorn main:app --reload --port 8000

# Alternative server
uvicorn fastapi_server:app --reload --port 8000
```

## 📖 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔧 Server Options

| File | Description | Use Case |
|------|-------------|----------|
| `run_BE.py` | Smart startup with dependency checks | Production & Development |
| `main.py` | Clean FastAPI with models | Primary development |
| `fastapi_server.py` | Comprehensive server | Full feature testing |
| `start_simple.py` | Minimal startup | Quick testing |

## Features

- **Product Management**: CRUD operations for products
- **Wishlist System**: Full wishlist management with Firebase
- **Firebase Integration**: Uses Firebase Admin SDK for database operations
- **Search & Filtering**: Advanced product search with semantic search
- **Recommendation System**: AI-powered product recommendations
- **Chatbot Integration**: Customer support chatbot
- **RESTful APIs**: Clean and documented API endpoints
- **CORS Support**: Configured for frontend integration
- **Type Safety**: Pydantic models with validation
- **Async Support**: High-performance async/await implementation

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Firebase Admin SDK:
   - Download your Firebase service account key JSON file
   - Place it in this directory as `serviceAccountKey.json`

3. Run data migration (if needed):
```bash
python migrate_to_firebase.py
```

## Running the Server

### Recommended Method
```bash
python run_BE.py
```

### Alternative Methods
```bash
# Main server
python main.py

# Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Products
- `GET /products` - Get all products
- `GET /products/featured` - Get featured products
- `GET /products/top-this-week` - Get top products
- `GET /products/{id}` - Get specific product
- `GET /search` - Search products

### Wishlists
- `GET /api/wishlist` - Get user wishlists
- `POST /api/wishlist` - Create wishlist
- `DELETE /api/wishlist/{id}` - Delete wishlist
- `POST /api/wishlist/{id}/products` - Add product to wishlist
- `DELETE /api/wishlist/{id}/products/{pid}` - Remove product

### Recommendations
- `GET /recommendations` - Get personalized recommendations
- `POST /events` - Track user events
- `GET /recommendation-health` - Check recommendation system

### Other
- `GET /categories` - Get product categories
- `GET /brands` - Get product brands
- `POST /chatbot` - Chatbot endpoint
- `GET /health` - Health check

## API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.
Visit `http://localhost:8000/redoc` for ReDoc documentation.
