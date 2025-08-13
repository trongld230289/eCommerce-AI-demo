from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    VIEW = "view"
    ADD_TO_CART = "add_to_cart"
    REMOVE_FROM_CART = "remove_from_cart"
    ADD_TO_WISHLIST = "add_to_wishlist"
    REMOVE_FROM_WISHLIST = "remove_from_wishlist"

class Product(BaseModel):
    id: Optional[int] = None
    name: str
    price: float
    original_price: Optional[float] = None
    imageUrl: str
    category: str
    description: Optional[str] = None
    brand: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    color: Optional[str] = None
    size: Optional[str] = None
    rating: Optional[float] = None
    is_new: Optional[bool] = False
    discount: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ProductCreate(BaseModel):
    name: str
    price: float
    original_price: Optional[float] = None
    imageUrl: str
    category: str
    description: Optional[str] = None
    brand: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    color: Optional[str] = None
    size: Optional[str] = None
    rating: Optional[float] = None
    is_new: Optional[bool] = False
    discount: Optional[float] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    imageUrl: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    tags: Optional[List[str]] = None
    color: Optional[str] = None
    size: Optional[str] = None
    rating: Optional[float] = None
    is_new: Optional[bool] = None
    discount: Optional[float] = None

class SearchFilters(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    keywords: Optional[str] = None
    tags: Optional[List[str]] = None

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class UserEvent(BaseModel):
    event_type: EventType
    user_id: str
    product_id: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class UserEventCreate(BaseModel):
    event_type: EventType
    user_id: str
    product_id: str
    metadata: Optional[Dict[str, Any]] = None

class UserEventResponse(BaseModel):
    success: bool
    message: str
    event_id: Optional[str] = None

class ChatbotRequest(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatbotResponse(BaseModel):
    response: str
    products: List[Product] = Field(default_factory=list)
    search_params: Dict[str, Any] = Field(default_factory=dict)
    redirect_url: Optional[str] = None
    page_code: Optional[str] = None
    smart_search_used: Optional[bool] = False
    parsed_filters: Dict[str, Any] = Field(default_factory=dict)

class SmartSearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10

class SmartSearchResponse(BaseModel):
    query: str
    results: List[Product] = Field(default_factory=list)
    parsed_filters: Dict[str, Any] = Field(default_factory=dict)
    total_found: int
    search_type: str
    timestamp: str
