from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from models import (
    WishlistRecommendationRequest, ProductSuggestion, 
    WishlistRecommendation, WishlistRecommendationResponse
)
from services.wishlist_recommendations_service import wishlist_recommendations_service

router = APIRouter(prefix="/api/wishlist", tags=["wishlist-recommendations"])

class SingleProductRequest(BaseModel):
    user_id: str
    product_id: int

@router.post("/recommendation/single", response_model=Dict[str, Any])
async def get_single_product_recommendation(
    request: SingleProductRequest
):
    """
    Get recommendation for a single product - faster response for individual items.
    
    This API:
    1. Takes single product_id instead of array
    2. Faster processing - no batch overhead  
    3. Better for FE to call multiple times in parallel
    4. Returns single recommendation or null if no match
    """
    try:
        print(f"🔍 Single recommendation for user: {request.user_id}, product: {request.product_id}")
        
        # Use existing service but with single product
        recommendations = await wishlist_recommendations_service.get_recommendations(
            user_id=request.user_id,
            all_product_ids=[request.product_id]  # Single product in array
        )
        
        # Return single recommendation or null
        if recommendations:
            return {
                "status": "success",
                "recommendation": recommendations[0]
            }
        else:
            return {
                "status": "success", 
                "recommendation": None,
                "message": "No same-category recommendations found"
            }
        
    except Exception as e:
        print(f"Error in single product recommendation: {str(e)}")
        return {
            "status": "error",
            "recommendation": None,
            "error": str(e)
        }

@router.post("/recommendations", response_model=WishlistRecommendationResponse)
async def get_wishlist_recommendations(
    request: WishlistRecommendationRequest
):
    """
    Get wishlist recommendations based on user's current wishlist products.
    Enhanced version with async support and improved filtering.
    
    This API:
    1. Gets all shared wishlists from the database (excludes current user's shared wishlists)
    2. Collects all product IDs from all user's wishlist tabs in single call
    3. Uses async RAG to analyze products and generate upgrade suggestions
    4. Avoids self-recommendations by filtering duplicate products
    5. Returns recommendations with product details and suggestion messages
    """
    try:
        if not request.product_ids:
            return WishlistRecommendationResponse(
                status="success",
                recommendations=[],
                total_recommendations=0
            )
        
        # Get user_id from frontend request (required for excluding user's shared wishlists)
        user_id = request.user_id or 'anonymous'
        print(f"🔍 Getting recommendations for user: {user_id}")
        print(f"📝 Product IDs: {request.product_ids}")
        
        # Use async version with enhanced filtering
        recommendations = await wishlist_recommendations_service.get_recommendations(
            user_id=user_id,  # This will exclude shared wishlists from this user
            all_product_ids=request.product_ids  # Now expects ALL product IDs from all tabs
        )
        
        return WishlistRecommendationResponse(
            status="success",
            recommendations=recommendations,
            total_recommendations=len(recommendations)
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get wishlist recommendations: {str(e)}"
        )

@router.post("/test-shared-products")
async def test_shared_products():
    """Test endpoint to check shared wishlist products (no auth required)"""
    try:
        shared_products = wishlist_recommendations_service._get_shared_products_from_service()
        return {
            "status": "success",
            "total_products": len(shared_products),
            "products": shared_products[:5] if shared_products else []  # Return first 5 for preview
        }
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e)
        }

@router.post("/test-recommendations")
async def test_recommendations():
    """Test endpoint for recommendations (no auth required)"""
    try:
        # Test with some sample product IDs
        test_product_ids = [33, 4, 41]  # Based on the shared products we saw
        recommendations = wishlist_recommendations_service.get_recommendations(
            user_id="test_user",
            product_ids=test_product_ids
        )
        
        return {
            "status": "success",
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e)
        }
