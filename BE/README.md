# eCommerce Backend API

A Python FastAPI backend service for the eCommerce application with Firebase integration.

## Features

- **Product Management**: CRUD operations for products
- **Firebase Integration**: Uses Firebase Admin SDK for database operations
- **Search & Filtering**: Advanced product search with multiple filters
- **RESTful APIs**: Clean and documented API endpoints
- **CORS Support**: Configured for frontend integration

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Firebase Admin SDK:
   - Download your Firebase service account key JSON file
   - Place it in this directory as `firebase-service-account.json`
   - Or set the path in environment variables

3. Create `.env` file:
```env
FIREBASE_SERVICE_ACCOUNT_PATH=./firebase-service-account.json
```

## Running the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /products` - Get all products
- `GET /products/{product_id}` - Get product by ID
- `POST /products` - Create new product
- `PUT /products/{product_id}` - Update product
- `DELETE /products/{product_id}` - Delete product
- `GET /search` - Search products with filters
- `GET /categories` - Get all categories
- `GET /brands` - Get all brands

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.
