from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel
import random
from models import Product, RecommendationResponse
from data import products_data, user_preferences, user_recommendations, default_recommendations, category_recommendations
from chatbot_service import process_chatbot_query

app = FastAPI(
    title="eCommerce Recommendation API",
    description="API for product recommendations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to get products by IDs
def get_products_by_ids(product_ids: List[int]) -> List[Product]:
    """Get products by their IDs"""
    return [product for product in products_data if product.id in product_ids]

@app.get("/")
async def root():
    return {"message": "eCommerce Recommendation API"}

@app.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    user_id: Optional[str] = Query(None, description="User ID for personalized recommendations"),
    limit: int = Query(default=10, ge=1, le=50, description="Number of recommendations to return")
):
    """
    Get product recommendations for a user.
    If user_id is provided, returns personalized recommendations.
    If user_id is null, returns default popular products.
    """
    
    if user_id and user_id in user_recommendations:
        # Get specific curated recommendations for the user
        recommended_product_ids = user_recommendations[user_id]
        recommended_products = get_products_by_ids(recommended_product_ids)
        
        # If we need more products to reach the limit, add preference-based products
        if len(recommended_products) < limit and user_id in user_preferences:
            user_prefs = user_preferences[user_id]
            preferred_categories = user_prefs.get("preferred_categories", [])
            preferred_brands = user_prefs.get("preferred_brands", [])
            
            # Get additional products based on preferences
            additional_products = []
            for product in products_data:
                if (product.id not in recommended_product_ids and
                    (product.category in preferred_categories or 
                     product.brand in preferred_brands)):
                    additional_products.append(product)
            
            # Sort by rating and add to recommendations
            additional_products.sort(key=lambda x: x.rating, reverse=True)
            recommended_products.extend(additional_products[:limit - len(recommended_products)])
        
        return RecommendationResponse(
            products=recommended_products[:limit],
            is_personalized=True,
            user_id=user_id
        )
    
    elif user_id and user_id in user_preferences:
        # Fallback to preference-based recommendations
        user_prefs = user_preferences[user_id]
        preferred_categories = user_prefs.get("preferred_categories", [])
        preferred_brands = user_prefs.get("preferred_brands", [])
        
        # Filter products based on user preferences
        recommended_products = []
        
        # First, add products from preferred categories and brands
        for product in products_data:
            if (product.category in preferred_categories or 
                product.brand in preferred_brands):
                recommended_products.append(product)
        
        # If we don't have enough recommendations, add popular products
        if len(recommended_products) < limit:
            remaining_products = [p for p in products_data if p not in recommended_products]
            # Sort by rating (popularity)
            remaining_products.sort(key=lambda x: x.rating, reverse=True)
            recommended_products.extend(remaining_products[:limit - len(recommended_products)])
        
        # Shuffle to add some variety
        random.shuffle(recommended_products)
        
        return RecommendationResponse(
            products=recommended_products[:limit],
            is_personalized=True,
            user_id=user_id
        )
    
    else:
        # Return default curated recommendations for anonymous users
        recommended_products = get_products_by_ids(default_recommendations)
        
        # If we need more products, add popular ones
        if len(recommended_products) < limit:
            remaining_products = [p for p in products_data if p.id not in default_recommendations]
            remaining_products.sort(key=lambda x: x.rating, reverse=True)
            recommended_products.extend(remaining_products[:limit - len(recommended_products)])
        
        return RecommendationResponse(
            products=recommended_products[:limit],
            is_personalized=False,
            user_id=None
        )

@app.get("/recommendations/category/{category}", response_model=RecommendationResponse)
async def get_category_recommendations(
    category: str,
    limit: int = Query(default=5, ge=1, le=20, description="Number of recommendations to return")
):
    """
    Get product recommendations based on a category for cross-selling.
    """
    if category in category_recommendations:
        recommended_product_ids = category_recommendations[category]
        recommended_products = get_products_by_ids(recommended_product_ids)
        
        # If we need more products, add popular ones from related categories
        if len(recommended_products) < limit:
            remaining_products = [p for p in products_data if p.id not in recommended_product_ids]
            remaining_products.sort(key=lambda x: x.rating, reverse=True)
            recommended_products.extend(remaining_products[:limit - len(recommended_products)])
        
        return RecommendationResponse(
            products=recommended_products[:limit],
            is_personalized=False,
            user_id=None
        )
    else:
        # Return popular products if category not found
        popular_products = sorted(products_data, key=lambda x: x.rating, reverse=True)
        return RecommendationResponse(
            products=popular_products[:limit],
            is_personalized=False,
            user_id=None
        )

@app.get("/products", response_model=List[Product])
async def get_all_products():
    """Get all available products"""
    return products_data

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """Get a specific product by ID"""
    for product in products_data:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

# Chatbot models
class ChatbotRequest(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatbotResponse(BaseModel):
    response: str
    products: List[Product]
    search_params: dict

@app.post("/chatbot", response_model=ChatbotResponse)
async def chatbot_query(request: ChatbotRequest):
    """
    Process chatbot queries using OpenAI function calling to extract product search parameters
    """
    try:
        result = await process_chatbot_query(request.message)
        return ChatbotResponse(
            response=result["response"],
            products=result["products"],
            search_params=result["search_params"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search", response_model=List[Product])
async def search_products_endpoint(
    category: Optional[str] = Query(None, description="Product category"),
    brand: Optional[str] = Query(None, description="Product brand"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    keywords: Optional[str] = Query(None, description="Keywords (comma-separated)")
):
    """
    Direct product search endpoint
    """
    from chatbot_service import search_products
    
    keyword_list = None
    if keywords:
        keyword_list = [k.strip() for k in keywords.split(",")]
    
    products = search_products(
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        keywords=keyword_list
    )
    
    return products

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
