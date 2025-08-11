from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from models import Product, ProductCreate, ProductUpdate, SearchFilters, ApiResponse, ChatbotRequest, ChatbotResponse, SmartSearchRequest, SmartSearchResponse
from product_service import product_service
from product_service_v2 import product_service_v2
import uvicorn
import httpx
import json
from datetime import datetime

app = FastAPI(
    title="eCommerce Backend API",
    description="Backend API for eCommerce application with Firebase integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "eCommerce Backend API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

# Product endpoints
@app.get("/products", response_model=List[dict])
async def get_products():
    """Get all products"""
    try:
        products = product_service.get_all_products()
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving products: {str(e)}")

# Featured and top products endpoints
@app.get("/products/featured")
async def get_featured_products(limit: Optional[int] = Query(6, ge=1)):
    try:
        products = product_service_v2.get_featured_products(limit)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    """Get product by ID"""
    try:
        product = product_service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving product: {str(e)}")

@app.post("/products")
async def create_product(product: ProductCreate):
    """Create a new product"""
    try:
        result = product_service.create_product(product)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create product"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")

@app.put("/products/{product_id}")
async def update_product(product_id: int, product: ProductUpdate):
    """Update a product"""
    try:
        result = product_service.update_product(product_id, product)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to update product"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating product: {str(e)}")

@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
    """Delete a product"""
    try:
        result = product_service.delete_product(product_id)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to delete product"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting product: {str(e)}")

# Search endpoint
@app.get("/search")
async def search_products(
    category: Optional[str] = Query(None, description="Product category"),
    brand: Optional[str] = Query(None, description="Product brand"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    keywords: Optional[str] = Query(None, description="Keywords (comma-separated)")
):
    """Search products with filters"""
    try:
        filters = SearchFilters(
            category=category,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            keywords=keywords
        )
        products = product_service.search_products(filters)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching products: {str(e)}")



@app.get("/products/top-this-week")
async def get_top_products_this_week(limit: int = Query(6, description="Number of top products to return")):
    """Get top products this week based on views and sales"""
    try:
        all_products = product_service.get_all_products()
        
        # Calculate popularity score based on views and sales
        products_with_score = []
        max_sales = max(p.get('weeklySales', 0) for p in all_products) or 1
        max_views = max(p.get('weeklyViews', 0) for p in all_products) or 1
        
        for product in all_products:
            weekly_sales = product.get('weeklySales', 0)
            weekly_views = product.get('weeklyViews', 0)
            
            # Weight: 70% weekly sales, 30% weekly views (normalized)
            sales_score = (weekly_sales / max_sales) * 0.7
            views_score = (weekly_views / max_views) * 0.3
            popularity_score = sales_score + views_score
            
            product['popularity_score'] = popularity_score
            products_with_score.append(product)
        
        # Sort by popularity score and return top products
        products_with_score.sort(key=lambda x: x['popularity_score'], reverse=True)
        return products_with_score[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving top products: {str(e)}")

# Category and brand endpoints
@app.get("/categories")
async def get_categories():
    """Get all product categories"""
    try:
        categories = product_service.get_categories()
        return {"categories": ["All"] + categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving categories: {str(e)}")

@app.get("/brands")
async def get_brands():
    """Get all product brands"""
    try:
        brands = product_service.get_brands()
        return {"brands": ["All"] + brands}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving brands: {str(e)}")

# Chatbot endpoint
@app.post("/chatbot", response_model=ChatbotResponse)
async def chatbot_endpoint(request: ChatbotRequest):
    """Process chatbot messages and return responses with product recommendations"""
    try:
        message = request.message.lower()
        
        # Simple chatbot logic for demonstration
        # In a real implementation, this would use NLP/AI services
        response_text = "Hello! I'm here to help you find products. What are you looking for?"
        products = []
        search_params = {}
        page_code = "others"
        
        # Basic product search logic
        if any(keyword in message for keyword in ["laptop", "computer", "pc"]):
            products = product_service.search_products(SearchFilters(category="Electronics"))
            search_params = {"category": "Electronics", "keywords": "laptop"}
            response_text = "I found some laptops for you!"
            page_code = "products"
        elif any(keyword in message for keyword in ["phone", "smartphone", "mobile"]):
            products = product_service.search_products(SearchFilters(category="Electronics"))
            search_params = {"category": "Electronics", "keywords": "phone"}
            response_text = "Here are some smartphones I found!"
            page_code = "products"
        elif any(keyword in message for keyword in ["headphones", "headset", "earphones"]):
            products = product_service.search_products(SearchFilters(category="Electronics"))
            search_params = {"category": "Electronics", "keywords": "headphones"}
            response_text = "Check out these headphones!"
            page_code = "products"
        elif any(keyword in message for keyword in ["help", "hello", "hi"]):
            response_text = "Hello! I can help you find laptops, phones, headphones, and other electronics. What are you looking for?"
        
        return ChatbotResponse(
            response=response_text,
            products=products[:5],  # Limit to 5 products
            search_params=search_params,
            page_code=page_code
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chatbot request: {str(e)}")

# Smart search endpoint
@app.post("/search/smart", response_model=SmartSearchResponse)
async def smart_search_endpoint(request: SmartSearchRequest):
    """Perform intelligent search using the recommendation service"""
    try:
        # Forward the request to the recommendation service
        recommendation_url = "http://localhost:8001/search/smart"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                recommendation_url,
                json=request.dict(),
                headers={"Content-Type": "application/json"},
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            return SmartSearchResponse(
                query=result.get("query", request.query),
                results=result.get("results", []),
                parsed_filters=result.get("parsed_filters", {}),
                total_found=result.get("total_found", 0),
                search_type=result.get("search_type", "smart"),
                timestamp=datetime.now().isoformat()
            )
        else:
            # Fallback to regular search if recommendation service is unavailable
            # Simple keyword extraction
            keywords = request.query.lower()
            filters = SearchFilters(keywords=keywords)
            products = product_service.search_products(filters)
            
            return SmartSearchResponse(
                query=request.query,
                results=products[:request.limit],
                parsed_filters={"keywords": keywords},
                total_found=len(products),
                search_type="fallback",
                timestamp=datetime.now().isoformat()
            )
            
    except httpx.RequestError:
        # Fallback to regular search if recommendation service is unavailable
        keywords = request.query.lower()
        filters = SearchFilters(keywords=keywords)
        products = product_service.search_products(filters)
        
        return SmartSearchResponse(
            query=request.query,
            results=products[:request.limit],
            parsed_filters={"keywords": keywords},
            total_found=len(products),
            search_type="fallback",
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing smart search: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
