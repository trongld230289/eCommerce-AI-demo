from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from models import (Product, ProductCreate, ProductUpdate, SearchFilters, ApiResponse, 
                   ChatbotRequest, ChatbotResponse, SmartSearchRequest, SmartSearchResponse, 
                   Wishlist, WishlistCreate, WishlistAddProduct, Cart, CartAddItem, CartUpdateItem, CartRemoveItem,
                   UserEvent, UserEventCreate, RecommendationRequest, RecommendationResponse)
from product_service import product_service
from services.wishlist_service import wishlist_service
from services.cart_service import cart_service
from services.recommendation_service import recommendation_service
from routers.ai_router import router as ai_router
from routers.wishlist_router import router as wishlist_router
from routers.wishlist_recommendations_router import router as wishlist_recommendations_router
from routers.auth_router import router as auth_router
from routers.product_router import router as product_router
from routers.middleware_service_router import router as middleware_service_router
import uvicorn
import httpx
import json
import os
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

# Include routers
app.include_router(ai_router, prefix="/api", tags=["AI"])
app.include_router(wishlist_router, tags=["Wishlist"])
app.include_router(wishlist_recommendations_router, tags=["Wishlist Recommendations"])
app.include_router(auth_router, tags=["Auth"])
app.include_router(product_router, tags=["Products"])
app.include_router(middleware_service_router, tags=["Middleware"])

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

# Featured and top products endpoints - MUST come before /products/{product_id}
@app.get("/products/featured")
async def get_featured_products(limit: int = Query(6, ge=1, le=50, description="Number of featured products to return")):
    """Get featured products"""
    try:
        print(f"DEBUG: get_featured_products called with limit={limit}")
        all_products = product_service.get_all_products()
        print(f"DEBUG: Retrieved {len(all_products)} products from service")
        
        if not all_products:
            print("DEBUG: No products found, returning empty list")
            return []
        
        # Simple featured products selection - first N products or those marked as featured
        featured_products = []
        for product in all_products:
            if product.get('featured', False):
                featured_products.append(product)
        
        print(f"DEBUG: Found {len(featured_products)} featured products")
        
        if not featured_products:
            # If no featured products, return first few products
            featured_products = all_products[:limit]
            print(f"DEBUG: No featured products found, using first {len(featured_products)} products")
        else:
            # Sort by rating for best featured products first
            try:
                featured_products.sort(key=lambda x: float(x.get('rating', 0)), reverse=True)
                print("DEBUG: Successfully sorted featured products by rating")
            except Exception as sort_error:
                print(f"DEBUG: Error sorting products: {sort_error}")
                # Just return unsorted if sorting fails
        
        result = featured_products[:limit]
        print(f"DEBUG: Returning {len(result)} featured products")
        return result
        
    except Exception as e:
        print(f"ERROR in get_featured_products: {e}")
        import traceback
        traceback.print_exc()
        # Return a simple error response instead of raising HTTPException
        return {"error": f"Error retrieving featured products: {str(e)}"}

@app.get("/products/top-this-week")
async def get_top_products_this_week(limit: int = Query(6, ge=1, le=50, description="Number of top products to return")):
    """Get top products this week based on views and sales"""
    try:
        print(f"DEBUG: get_top_products_this_week called with limit={limit}")
        all_products = product_service.get_all_products()
        print(f"DEBUG: Retrieved {len(all_products)} products from service")
        
        if not all_products:
            print("DEBUG: No products found, returning empty list")
            return []
        
        # Simple popularity calculation with safe defaults
        products_with_score = []
        
        for i, product in enumerate(all_products):
            try:
                weekly_sales = int(product.get('weeklySales', 0))
                weekly_views = int(product.get('weeklyViews', 0))
                rating = float(product.get('rating', 0))
                
                # Simple popularity score: sales + views + rating
                popularity_score = weekly_sales + weekly_views + (rating * 10)
                
                # Create a clean copy of the product
                product_copy = dict(product)
                product_copy['popularity_score'] = popularity_score
                products_with_score.append(product_copy)
                
            except (ValueError, TypeError) as e:
                # Skip products with invalid data
                print(f"DEBUG: Skipping product {i} due to data error: {e}")
                continue
        
        print(f"DEBUG: Processed {len(products_with_score)} products with scores")
        
        # Sort by popularity score and return top products
        if products_with_score:
            try:
                products_with_score.sort(key=lambda x: x.get('popularity_score', 0), reverse=True)
                result = products_with_score[:limit]
                print(f"DEBUG: Returning {len(result)} top products")
                return result
            except Exception as sort_error:
                print(f"DEBUG: Error sorting products: {sort_error}")
                # Return unsorted if sorting fails
                return products_with_score[:limit]
        else:
            # Fallback: return first N products
            result = all_products[:limit]
            print(f"DEBUG: Fallback - returning first {len(result)} products")
            return result
            
    except Exception as e:
        print(f"ERROR in get_top_products_this_week: {e}")
        import traceback
        traceback.print_exc()
        # Return a simple error response instead of raising HTTPException
        return {"error": f"Error retrieving top products: {str(e)}"}

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

# Test endpoint
@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify server is working"""
    return {"message": "Server is working!", "timestamp": datetime.now().isoformat()}

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

# ---------------------- WISHLIST ENDPOINTS ----------------------
@app.get("/api/wishlist", response_model=List[Wishlist])
async def get_wishlist(user_id: str = Query(...)):
    """Get wishlist for a user"""
    try:
        wishlists = wishlist_service.get_user_wishlists(user_id)
        return wishlists
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching wishlist: {str(e)}")

@app.post("/api/wishlist", response_model=Wishlist)
async def create_wishlist(wishlist_data: WishlistCreate):
    """Create a new wishlist"""
    try:
        wishlist = wishlist_service.create_wishlist(wishlist_data)
        return wishlist
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating wishlist: {str(e)}")

@app.get("/api/wishlist/{wishlist_id}", response_model=Wishlist)
async def get_wishlist_by_id(wishlist_id: str, user_id: str = Query(...)):
    """Get a specific wishlist by ID"""
    try:
        wishlist = wishlist_service.get_wishlist(wishlist_id, user_id)
        if not wishlist:
            raise HTTPException(status_code=404, detail="Wishlist not found")
        return wishlist
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching wishlist: {str(e)}")

@app.post("/api/wishlist/{wishlist_id}/products", response_model=Wishlist)
async def add_product_to_wishlist(wishlist_id: str, product_data: WishlistAddProduct, user_id: str = Query(...)):
    """Add product to wishlist"""
    try:
        wishlist = wishlist_service.add_product_to_wishlist(wishlist_id, user_id, product_data.product_id)
        if not wishlist:
            raise HTTPException(status_code=404, detail="Wishlist not found")
        return wishlist
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding to wishlist: {str(e)}")

@app.delete("/api/wishlist/{wishlist_id}/products/{product_id}", response_model=Wishlist)
async def remove_product_from_wishlist(wishlist_id: str, product_id: int, user_id: str = Query(...)):
    """Remove product from wishlist"""
    try:
        wishlist = wishlist_service.remove_product_from_wishlist(wishlist_id, user_id, product_id)
        if not wishlist:
            raise HTTPException(status_code=404, detail="Wishlist not found")
        return wishlist
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing from wishlist: {str(e)}")

@app.delete("/api/wishlist/{wishlist_id}")
async def delete_wishlist(wishlist_id: str, user_id: str = Query(...)):
    """Delete a wishlist"""
    try:
        success = wishlist_service.delete_wishlist(wishlist_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Wishlist not found")
        return {"success": True, "message": "Wishlist deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting wishlist: {str(e)}")

# ---------------------- CART ENDPOINTS ----------------------
@app.get("/api/cart", response_model=Cart)
async def get_cart(user_id: str = Query(...)):
    """Get cart for a user"""
    try:
        cart = await cart_service.get_cart(user_id)
        return cart
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cart: {str(e)}")

@app.post("/api/cart/add", response_model=Cart)
async def add_item_to_cart(cart_item: CartAddItem, user_id: str = Query(...)):
    """Add item to cart"""
    try:
        cart = await cart_service.add_item_to_cart(user_id, cart_item)
        # Thuong implementation - add product to cart
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:8003/api/cart/add?user_id={user_id}",
                headers={"Content-Type": "application/json"},
                json={"product_id": cart_item.product_id, "quantity": cart_item.quantity}
            )
            if response.status_code != 200:
                print(f"Failed to push to external service: {response.text}")
        
        return cart
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding item to cart: {str(e)}")

@app.put("/api/cart/update", response_model=Cart)
async def update_cart_item(cart_item: CartUpdateItem, user_id: str = Query(...)):
    """Update item quantity in cart"""
    try:
        cart = await cart_service.update_item_quantity(user_id, cart_item)
        # Thuong implementation - update product quantity in cart
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"http://localhost:8003/api/cart/update?user_id={user_id}",
                headers={"Content-Type": "application/json"},
                json={"product_id": cart_item.product_id, "quantity": cart_item.quantity}
            )
            if response.status_code != 200:
                print(f"Failed to push to external service: {response.text}")

        return cart
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating cart item: {str(e)}")

@app.delete("/api/cart/remove", response_model=Cart)
async def remove_item_from_cart(cart_item: CartRemoveItem, user_id: str = Query(...)):
    """Remove item from cart"""
    try:
        cart = await cart_service.remove_item_from_cart(user_id, cart_item)
        # Thuong implementation - remove product from cart
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"http://localhost:8003/api/cart/remove?user_id={user_id}",
                headers={"Content-Type": "application/json"},
                json={"product_id": cart_item.product_id}
            )
            if response.status_code != 200:
                print(f"Failed to push to external service: {response.text}")

        return cart
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing item from cart: {str(e)}")

@app.delete("/api/cart/clear", response_model=Cart)
async def clear_cart(user_id: str = Query(...)):
    """Clear all items from cart"""
    try:
        cart = await cart_service.clear_cart(user_id)
        # Thuong implementation - clear cart
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"http://localhost:8003/api/cart/clear?user_id={user_id}"
            )
            if response.status_code != 200:
                print(f"Failed to push to external service: {response.text}")

        return cart
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cart: {str(e)}")

@app.post("/api/cart/sync", response_model=Cart)
async def sync_cart(frontend_cart: List[dict], user_id: str = Query(...)):
    """Sync cart from frontend localStorage to Firebase"""
    try:
        cart = await cart_service.sync_cart_from_frontend(user_id, frontend_cart)
        return cart
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing cart: {str(e)}")

# ===== RECOMMENDATION SYSTEM ENDPOINTS =====

@app.post("/api/recommendations/track")
async def track_user_event(event: UserEventCreate):
    """Track user event for recommendation system"""
    try:
        success = await recommendation_service.track_user_event(event)
        # Thuong implementation - push user event to external service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8003/api/events",
                json=event.model_dump()
            )
            if response.status_code != 200:
                raise ValueError(f"Failed to push event to external service: {response.status_code} - {response.text}")

        if success:
            return {"status": "success", "message": "Event tracked successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to track event")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking event: {str(e)}")

@app.get("/api/recommendations")
async def get_recommendations(
    user_id: Optional[str] = Query(None, description="User ID for personalized recommendations"),
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations to return"),
    category: Optional[str] = Query(None, description="Category to filter recommendations"),
    context: Optional[str] = Query(None, description="Context where recommendations are shown")
):
    """Get product recommendations for user or guest"""
    try:
        request = RecommendationRequest(
            user_id=user_id,
            limit=limit,
            category=category,
            context=context
        )
        
        recommendations = await recommendation_service.get_recommendations(request)
        
        # Convert to simple format for frontend
        return {
            "recommendations": recommendations.recommendations,
            "products": recommendations.recommendations,  # Alias for compatibility
            "user_id": recommendations.user_id,
            "source": recommendations.source,
            "context": recommendations.context,
            "count": recommendations.total_count,
            "timestamp": recommendations.timestamp
        }
        
    except Exception as e:
        print(f"Error in get_recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching recommendations: {str(e)}")

@app.get("/api/recommendations/{user_id}")
async def get_user_recommendations(
    user_id: str,
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations to return"),
    category: Optional[str] = Query(None, description="Category to filter recommendations"),
    context: Optional[str] = Query(None, description="Context where recommendations are shown")
):
    """Get personalized recommendations for a specific user"""
    try:
        request = RecommendationRequest(
            user_id=user_id,
            limit=limit,
            category=category,
            context=context
        )
        
        recommendations = await recommendation_service.get_recommendations(request)
        
        return {
            "recommendations": recommendations.recommendations,
            "products": recommendations.recommendations,  # Alias for compatibility
            "user_id": recommendations.user_id,
            "source": recommendations.source,
            "context": recommendations.context,
            "count": recommendations.total_count,
            "timestamp": recommendations.timestamp
        }
        
    except Exception as e:
        print(f"Error in get_user_recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching recommendations: {str(e)}")

@app.get("/api/recommendations/trending")
async def get_trending_products(
    limit: int = Query(10, ge=1, le=50, description="Number of trending products to return"),
    days_back: int = Query(7, ge=1, le=30, description="Number of days to look back for trending analysis")
):
    """Get trending products based on recent user activity"""
    try:
        trending = await recommendation_service.get_trending_recommendations(limit, days_back)
        
        return {
            "products": trending,
            "source": "trending",
            "count": len(trending),
            "days_analyzed": days_back
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trending products: {str(e)}")

@app.get("/api/users/{user_id}/events")
async def get_user_events(
    user_id: str,
    days_back: int = Query(30, ge=1, le=90, description="Number of days to look back")
):
    """Get user events for analysis"""
    try:
        events = await recommendation_service.get_user_events(user_id, days_back)
        
        return {
            "events": events,
            "user_id": user_id,
            "count": len(events),
            "days_analyzed": days_back
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user events: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
