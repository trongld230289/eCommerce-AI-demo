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
    PURCHASE = "purchase"

class ShareType(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    ANONYMOUS = "anonymous"

class Product(BaseModel):
    id: Optional[int] = None
    name: str
    price: float
    original_price: Optional[float] = None
    imageUrl: str
    category: str
    description: Optional[str] = None
    rating: Optional[float] = None
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
    rating: Optional[float] = None
    discount: Optional[float] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    imageUrl: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
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

class WishlistItem(BaseModel):
    product_id: int
    added_at: float

class WishlistItemWithDetails(BaseModel):
    product_id: int
    added_at: float
    product_details: Optional[Dict[str, Any]] = None

class Wishlist(BaseModel):
    id: str
    user_id: str
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    name: str
    products: List[WishlistItemWithDetails] = Field(default_factory=list)
    item_count: int = 0
    share_status: ShareType = ShareType.PRIVATE
    created_at: float
    updated_at: float

class WishlistCreate(BaseModel):
    name: str
    user_id: str
    user_email: Optional[str] = None
    user_name: Optional[str] = None

class WishlistUpdate(BaseModel):
    name: Optional[str] = None
    share_status: Optional[ShareType] = None

class WishlistAddProduct(BaseModel):
    product_id: int

class WishlistRemoveProduct(BaseModel):
    product_id: int

class WishlistShareUpdate(BaseModel):
    share_status: ShareType

class WishlistShareResponse(BaseModel):
    success: bool
    message: str
    share_status: ShareType
    share_url: Optional[str] = None

class WishlistSearchRequest(BaseModel):
    email: str

class WishlistSearchResult(BaseModel):
    id: str
    user_id: str
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    name: str
    item_count: int
    share_status: ShareType
    created_at: float
    updated_at: float

class WishlistSearchResponse(BaseModel):
    success: bool
    message: str
    wishlists: List[WishlistSearchResult] = Field(default_factory=list)

# Cart Models
class CartItem(BaseModel):
    product_id: int
    quantity: int
    added_at: float
    product_details: Optional[Dict[str, Any]] = None

class Cart(BaseModel):
    id: str
    user_id: str
    items: List[CartItem] = Field(default_factory=list)
    item_count: int = 0
    total_amount: float = 0.0
    created_at: float
    updated_at: float

class CartCreate(BaseModel):
    user_id: str

class CartAddItem(BaseModel):
    product_id: int
    quantity: int = 1

class CartUpdateItem(BaseModel):
    product_id: int
    quantity: int

class CartRemoveItem(BaseModel):
    product_id: int

# User Event Models for Recommendation System
class UserEvent(BaseModel):
    user_id: str
    event_type: EventType
    product_id: int
    session_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class UserEventCreate(BaseModel):
    user_id: str
    event_type: EventType
    product_id: int
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# Recommendation Models
class RecommendationRequest(BaseModel):
    user_id: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=50)
    category: Optional[str] = None
    context: Optional[str] = None  # "homepage", "product_detail", "cart", etc.

class RecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    user_id: Optional[str] = None
    source: str  # "personalized", "trending", "category_based", "fallback"
    context: Optional[str] = None
    total_count: int
    timestamp: datetime
