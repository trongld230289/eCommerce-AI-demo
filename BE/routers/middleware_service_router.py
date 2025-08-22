from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from pydantic import BaseModel
import sys
import os

# Add parent directory to sys.path to import from services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.middleware_service import simple_semantic_search, push_user_after_registration

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

class UserRegistrationRequest(BaseModel):
    userId: str
    userEmail: str
    userName: str

class UserRegistrationResponse(BaseModel):
    status: str
    message: str

@router.get("/middleware/health")
async def health_check():
    """
    Health check endpoint for middleware service.
    """
    return {"status": "healthy", "service": "middleware_service"}

@router.post("/middleware/push_user_after_registration", response_model=UserRegistrationResponse)
async def push_user_after_registration_endpoint(request: UserRegistrationRequest):
    """
    Process user registration data after successful account creation.
    This endpoint is called after Firebase user registration to perform additional processing.
    """
    try:
        result = push_user_after_registration(request.userId, request.userEmail, request.userName)
        
        if result["status"] == "success":
            return UserRegistrationResponse(
                status=result["status"],
                message=result["message"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except Exception as e:
        print(f"Error in push_user_after_registration endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"User registration processing failed: {str(e)}")
