from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
import random
import httpx
from datetime import datetime
from google.api_core.retry import Retry
from firebase_config import get_firestore_db

# Import routers
from routers.ai_router import router as ai_router
from routers.auth_router import router as auth_router
from routers.product_router import router as product_router
from routers.wishlist_router import router as wishlist_router

# Create FastAPI app
app = FastAPI(
    title="eCommerce Backend API",
    description="FastAPI backend for eCommerce application with Firebase integration",
    version="1.0.0"
)

# Include routers
app.include_router(ai_router, prefix="/api", tags=["AI"])
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(product_router, prefix="/api", tags=["Products"])
app.include_router(wishlist_router, prefix="/api", tags=["Wishlist"])

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------- Config ----------------------
RECOMMENDATION_API_URL = os.getenv("RECOMMENDATION_API_URL", "http://localhost:8001")
USE_FIREBASE = True  # Enable Firebase to read existing wishlist data

# Optional: avoid gRPC flakiness on Windows (set env outside too)
os.environ.setdefault("FIRESTORE_USE_GRPC", "false")

# Firestore retry/timeout settings
RETRY = Retry(initial=0.2, maximum=2.0, multiplier=2.0, deadline=5.0)
RPC_TIMEOUT = 3.0

# ---------------------- Pydantic Models ----------------------
class UserEvent(BaseModel):
    user_id: str
    event_type: str
    product_id: Optional[int] = None
    timestamp: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None

class WishlistCreate(BaseModel):
    name: str
    description: Optional[str] = ""

class ProductAdd(BaseModel):
    product_id: int

class ChatbotMessage(BaseModel):
    message: str
    user_id: Optional[str] = "default_user"

# ---------------------- Firestore access ----------------------

def load_products_from_json():
    """Load products from products.json file"""
    try:
        products_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'products.json')
        if os.path.exists(products_file):
            with open(products_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
                print(f"Loaded {len(products)} products from products.json")
                return products
        else:
            print("products.json file not found")
            return get_sample_products()
    except Exception as e:
        print(f"Error loading products from JSON: {e}")
        return get_sample_products()

def get_all_products_from_firestore(limit: int = 200):
    """Read products with retry + timeout; fall back to JSON then sample data."""
    if not USE_FIREBASE:
        # Try loading from products.json first, then fall back to sample data
        products = load_products_from_json()
        return products[:limit] if len(products) > limit else products

    try:
        db = get_firestore_db()
        if db is None:
            return load_products_from_json()

        print("Attempting to fetch products from Firestore…")
        q = db.collection("products").order_by("id").limit(limit)
        docs = q.stream(retry=RETRY, timeout=RPC_TIMEOUT)

        products = []
        for d in docs:
            p = d.to_dict() or {}
            # Prefer stored numeric id; otherwise use doc id (string)
            p["id"] = p.get("id", d.id)
            products.append(p)

        if not products:
            print("No products found in Firestore, loading from JSON")
            return load_products_from_json()
        print(f"Fetched {len(products)} products from Firestore")
        return products
    except Exception as e:
        print(f"Error fetching products from Firestore: {e}")
        return load_products_from_json()

def get_product_by_id_from_firestore(product_id):
    if not USE_FIREBASE:
        # Try loading from products.json first
        products = load_products_from_json()
        return next((p for p in products if str(p["id"]) == str(product_id)), None)

    try:
        db = get_firestore_db()
        if db is None:
            products = load_products_from_json()
            return next((p for p in products if str(p["id"]) == str(product_id)), None)

        doc = db.collection("products").document(str(product_id)).get(timeout=RPC_TIMEOUT)
        if doc.exists:
            p = doc.to_dict() or {}
            p["id"] = p.get("id", doc.id)
            return p
        else:
            # Fall back to JSON
            products = load_products_from_json()
            return next((p for p in products if str(p["id"]) == str(product_id)), None)
    except Exception as e:
        print(f"Error fetching product {product_id} from Firestore: {e}")
        products = load_products_from_json()
        return next((p for p in products if str(p["id"]) == str(product_id)), None)

# ---------------------- Recommendation System Integration ----------------------

async def send_user_event_to_recommendation_system(user_id, event_type, product_data):
    """Send user event to recommendation system"""
    try:
        payload = {
            "user_id": user_id,
            "event_type": event_type,
            "product_data": product_data,
            "timestamp": datetime.now().isoformat()
        }
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{RECOMMENDATION_API_URL}/api/user-events",
                json=payload
            )
            
        if response.status_code == 200:
            print(f"✅ Event sent: {event_type} for user {user_id}")
            return True
        else:
            print(f"⚠️ Failed to send event: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error sending event to recommendation system: {e}")
        return False

async def get_user_recommendations_from_system(user_id, limit=5):
    """Get recommendations from recommendation system"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{RECOMMENDATION_API_URL}/api/recommendations/{user_id}?limit={limit}")
        return response.json() if response.status_code == 200 else []
    except:
        return []

async def smart_search_from_recommendation_system(query, limit=10):
    """Search products using semantic search from recommendation system"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{RECOMMENDATION_API_URL}/api/semantic-search",
                json={"query": query, "limit": limit}
            )
        
        if response.status_code == 200:
            results = response.json()
            return results.get("products", [])
        else:
            print(f"Semantic search failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error in semantic search: {e}")
        return []

# ---------------------- Sample Data ----------------------

def get_sample_products():
    """Get sample products for testing"""
    return [
        {
            "id": 1,
            "name": "iPhone 15 Pro",
            "price": 999.99,
            "category": "Electronics",
            "brand": "Apple",
            "description": "Latest iPhone with A17 Pro chip",
            "image": "https://example.com/iphone15pro.jpg",
            "rating": 4.8,
            "inStock": True,
            "weeklySales": 150,
            "weeklyViews": 2500
        },
        {
            "id": 2,
            "name": "Samsung Galaxy S24",
            "price": 899.99,
            "category": "Electronics",
            "brand": "Samsung",
            "description": "Flagship Android smartphone",
            "image": "https://example.com/galaxys24.jpg",
            "rating": 4.7,
            "inStock": True,
            "weeklySales": 120,
            "weeklyViews": 2100
        }
    ]

# ---------------------- API Routes ----------------------

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/products")
async def get_products(limit: int = Query(100, ge=1, le=500)):
    """Get all products"""
    try:
        products = get_all_products_from_firestore(limit)
        return {"products": products, "count": len(products)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")

@app.get("/products/featured")
async def get_featured_products():
    """Get featured products"""
    try:
        products = get_all_products_from_firestore()
        # Simple logic: products with rating >= 4.5
        featured = [p for p in products if p.get("rating", 0) >= 4.5]
        return {"products": featured[:10]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching featured products: {str(e)}")

@app.get("/products/top-this-week")
async def get_top_products_this_week():
    """Get top products this week based on sales and views"""
    try:
        products = get_all_products_from_firestore()
        # Calculate weighted score
        max_sales = max((p.get("weeklySales", 0) for p in products), default=0)
        max_views = max((p.get("weeklyViews", 0) for p in products), default=0)
        
        for p in products:
            sales_score = p.get("weeklySales", 0) / max_sales if max_sales > 0 else 0
            views_score = p.get("weeklyViews", 0) / max_views if max_views > 0 else 0
            p["weeklyScore"] = (sales_score * 0.7) + (views_score * 0.3)
        
        # Sort by weekly score and return top 10
        top_products = sorted(products, key=lambda x: x.get("weeklyScore", 0), reverse=True)[:10]
        return {"products": top_products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching top products: {str(e)}")

@app.get("/products/{product_id}")
async def get_product(product_id: int = Path(..., ge=1)):
    """Get a specific product by ID"""
    try:
        product = get_product_by_id_from_firestore(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"product": product}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching product: {str(e)}")

@app.get("/search")
async def search_products(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=100)):
    """Search products with semantic search or fallback to basic search"""
    try:
        # Try semantic search first
        semantic_results = await smart_search_from_recommendation_system(q, limit)
        
        if semantic_results:
            return {"products": semantic_results, "search_type": "semantic"}
        
        # Fallback to basic search
        products = get_all_products_from_firestore()
        query_lower = q.lower()
        
        filtered = [
            p for p in products
            if query_lower in p.get("name", "").lower() or
               query_lower in p.get("description", "").lower() or
               query_lower in p.get("category", "").lower() or
               query_lower in p.get("brand", "").lower()
        ]
        
        return {"products": filtered[:limit], "search_type": "basic"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/categories")
async def get_categories():
    """Get all product categories"""
    try:
        products = get_all_products_from_firestore()
        categories = list(set(p.get("category", "Unknown") for p in products))
        return {"categories": sorted(categories)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")

@app.get("/brands")
async def get_brands():
    """Get all product brands"""
    try:
        products = get_all_products_from_firestore()
        brands = list(set(p.get("brand", "Unknown") for p in products))
        return {"brands": sorted(brands)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching brands: {str(e)}")

@app.get("/recommendations")
async def get_recommendations(user_id: str = Query(...), limit: int = Query(5, ge=1, le=20)):
    """Get personalized recommendations for a user"""
    try:
        recommendations = await get_user_recommendations_from_system(user_id, limit)
        return {"recommendations": recommendations, "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recommendations: {str(e)}")

@app.post("/events")
async def track_user_event(event: UserEvent):
    """Track user events for recommendations"""
    try:
        # Send to recommendation system
        await send_user_event_to_recommendation_system(
            event.user_id,
            event.event_type,
            {"product_id": event.product_id} if event.product_id else {}
        )
        
        return {"status": "success", "message": "Event tracked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking event: {str(e)}")

@app.get("/events/{user_id}")
async def get_user_events(user_id: str):
    """Get user events history"""
    # This would typically fetch from a database
    return {"user_id": user_id, "events": [], "message": "Events endpoint - implement as needed"}

@app.get("/events/analytics/{user_id}")
async def get_user_analytics(user_id: str):
    """Get user analytics"""
    # Sample analytics data
    analytics = {
        "user_id": user_id,
        "total_events": 0,
        "product_views": 0,
        "purchases": 0,
        "wishlist_actions": 0,
        "search_queries": 0
    }
    return {"analytics": analytics}

@app.get("/recommendation-health")
async def check_recommendation_system_health():
    """Check if recommendation system is healthy"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{RECOMMENDATION_API_URL}/health")
        
        if response.status_code == 200:
            return {"status": "healthy", "recommendation_system": "online"}
        else:
            return {"status": "degraded", "recommendation_system": "offline"}
    except:
        return {"status": "degraded", "recommendation_system": "offline"}

@app.post("/chatbot")
async def chatbot_endpoint(message: ChatbotMessage):
    """Chatbot endpoint"""
    try:
        # Simple echo response - replace with actual chatbot logic
        response_text = f"Echo: {message.message}"
        
        return {
            "response": response_text,
            "user_id": message.user_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")

# ---------------------- Wishlist Management ----------------------

# In-memory storage for demo (replace with database in production)
demo_wishlists = []
demo_wishlist_counter = 1

def enhance_wishlist_with_product_details(wishlist):
    """Enhance wishlist products with full product details"""
    if not wishlist or "products" not in wishlist:
        return wishlist
    
    print(f"Debug: Enhancing wishlist {wishlist.get('id')} with {len(wishlist['products'])} products")
    
    for item in wishlist["products"]:
        if isinstance(item, dict) and "product_id" in item:
            product_id = item["product_id"]
            # Get full product details
            full_product = get_product_by_id_from_firestore(product_id)
            if full_product:
                # Create enhanced product object with wishlist metadata
                enhanced_product = full_product.copy()
                enhanced_product["added_to_wishlist_at"] = item.get("added_at", "")
                enhanced_product["wishlist_product_id"] = item.get("id", product_id)
                
                # Replace the item with enhanced product
                item.clear()
                item.update(enhanced_product)
    
    return wishlist

@app.get("/api/wishlist")
async def get_user_wishlists(user_id: str = Query("demo_user")):
    """Get all wishlists for a user"""
    try:
        user_wishlists = [w for w in demo_wishlists if w.get("user_id") == user_id]
        
        # Enhance each wishlist with product details
        enhanced_wishlists = [enhance_wishlist_with_product_details(w) for w in user_wishlists]
        
        return {
            "wishlists": enhanced_wishlists,
            "count": len(enhanced_wishlists),
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching wishlists: {str(e)}")

@app.post("/api/wishlist")
async def create_wishlist(wishlist_data: WishlistCreate, user_id: str = Query("demo_user")):
    """Create a new wishlist"""
    global demo_wishlist_counter
    
    try:
        new_wishlist = {
            "id": f"wishlist_{demo_wishlist_counter}",
            "name": wishlist_data.name,
            "description": wishlist_data.description,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "products": []
        }
        
        demo_wishlists.append(new_wishlist)
        demo_wishlist_counter += 1
        
        return {
            "message": "Wishlist created successfully",
            "wishlist": new_wishlist
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating wishlist: {str(e)}")

@app.post("/api/wishlist/{wishlist_id}/products")
async def add_product_to_wishlist(wishlist_id: str, product_data: ProductAdd):
    """Add a product to a wishlist"""
    try:
        # Find the wishlist
        wishlist = next((w for w in demo_wishlists if w["id"] == wishlist_id), None)
        if not wishlist:
            raise HTTPException(status_code=404, detail="Wishlist not found")
        
        # Check if product exists
        product = get_product_by_id_from_firestore(product_data.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if product already in wishlist
        existing = next((p for p in wishlist["products"] if p.get("product_id") == product_data.product_id), None)
        if existing:
            return {"message": "Product already in wishlist", "wishlist": wishlist}
        
        # Add product to wishlist
        wishlist_item = {
            "id": f"item_{len(wishlist['products']) + 1}",
            "product_id": product_data.product_id,
            "added_at": datetime.now().isoformat()
        }
        
        wishlist["products"].append(wishlist_item)
        
        # Enhance with product details for response
        enhanced_wishlist = enhance_wishlist_with_product_details(wishlist)
        
        return {
            "message": "Product added to wishlist successfully",
            "wishlist": enhanced_wishlist
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding product to wishlist: {str(e)}")

@app.delete("/api/wishlist/{wishlist_id}/products/{product_id}")
async def remove_product_from_wishlist(wishlist_id: str, product_id: int):
    """Remove a product from a wishlist"""
    try:
        # Find the wishlist
        wishlist = next((w for w in demo_wishlists if w["id"] == wishlist_id), None)
        if not wishlist:
            raise HTTPException(status_code=404, detail="Wishlist not found")
        
        # Remove the product
        original_length = len(wishlist["products"])
        wishlist["products"] = [p for p in wishlist["products"] if p.get("product_id") != product_id]
        
        if len(wishlist["products"]) == original_length:
            raise HTTPException(status_code=404, detail="Product not found in wishlist")
        
        # Enhance with product details for response
        enhanced_wishlist = enhance_wishlist_with_product_details(wishlist)
        
        return {
            "message": "Product removed from wishlist successfully",
            "wishlist": enhanced_wishlist
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing product from wishlist: {str(e)}")

@app.delete("/api/wishlist/{wishlist_id}")
async def delete_wishlist(wishlist_id: str):
    """Delete a wishlist"""
    global demo_wishlists
    
    try:
        # Find and remove the wishlist
        original_length = len(demo_wishlists)
        demo_wishlists = [w for w in demo_wishlists if w["id"] != wishlist_id]
        
        if len(demo_wishlists) == original_length:
            raise HTTPException(status_code=404, detail="Wishlist not found")
        
        return {"message": "Wishlist deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting wishlist: {str(e)}")

@app.get("/api/wishlist/{wishlist_id}/debug")
async def debug_wishlist_route(wishlist_id: str):
    """Debug endpoint for wishlist"""
    wishlist = next((w for w in demo_wishlists if w["id"] == wishlist_id), None)
    return {
        "wishlist_found": wishlist is not None,
        "wishlist": wishlist,
        "all_wishlists": demo_wishlists
    }

@app.post("/api/test")
async def test_post():
    """Test POST endpoint"""
    return {"message": "POST endpoint working!", "timestamp": datetime.now().isoformat()}

# ---------------------- Startup Event ----------------------

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    print("🚀 Starting eCommerce FastAPI Server…")
    print("📍 Server will be available at: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    print("📋 Registered routes:")
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = ", ".join(route.methods)
            print(f"  {route.path} -> {methods}")
    print("-" * 50)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
