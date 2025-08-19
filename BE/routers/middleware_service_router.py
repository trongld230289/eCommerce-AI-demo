from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from pydantic import BaseModel
import sys
import os

# Add parent directory to sys.path to import from services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.middleware_service import simple_semantic_search

router = APIRouter()

class SimpleSearchRequest(BaseModel):
    query: str
    limit: int = 10

class ProductResponse(BaseModel):
    id: str
    name: str
    category: str
    price: float
    original_price: float
    rating: float
    discount: float
    imageUrl: str
    similarity_score: float

class SimpleSearchResponse(BaseModel):
    status: str
    products: List[ProductResponse]
    total_results: int

@router.get("/middleware/search")
async def simple_search_get(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum number of results")
):
    """
    Simple semantic search using query parameter.
    Returns a list of products matching the search query.
    """
    try:
        products = simple_semantic_search(q, limit)
        return {
            "status": "success",
            "products": products,
            "total_results": len(products)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/middleware/search", response_model=SimpleSearchResponse)
async def simple_search_post(search_request: SimpleSearchRequest):
    """
    Simple semantic search using POST request.
    Returns a list of products matching the search query.
    """
    try:
        products = simple_semantic_search(search_request.query, search_request.limit)
        
        # Convert to response model
        product_responses = [ProductResponse(**product) for product in products]
        
        return SimpleSearchResponse(
            status="success",
            products=product_responses,
            total_results=len(products)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/middleware/health")
async def health_check():
    """
    Health check endpoint for middleware service.
    """
    return {"status": "healthy", "service": "middleware_service"}
