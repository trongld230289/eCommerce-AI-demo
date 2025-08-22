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

class RecommendationSourceEnum(str, Enum):
    PERSONALIZED = "personalized"
    TOGETHER = "together"
    CATEGORY = "category"
    TRENDING = "trending"
    RATING = "rating"
    DESCRIPTION = "description"
    WISHLIST = "wishlist"
    PURCHASE = "purchase"
    SAME_TASTE = "same_taste"
    PRODUCT = "product"
    GIFT = "gift"

# Centralized mapping from algorithm label to RecommendationSourceEnum
ALGORITHM_TO_REC_SOURCE = {
    "top_item_to_item": RecommendationSourceEnum.PERSONALIZED.value,
    "top_als": RecommendationSourceEnum.SAME_TASTE.value,
    "top_pagerank": RecommendationSourceEnum.SAME_TASTE.value,
    "fit_description": RecommendationSourceEnum.DESCRIPTION.value,
    "most_added_to_wishlist": RecommendationSourceEnum.WISHLIST.value,
    "most_purchased": RecommendationSourceEnum.PURCHASE.value,
}

class Product(BaseModel):
    id: Optional[int] = None
    name: str
    title: Optional[str] = None  # Add title field for compatibility
    price: float
    original_price: Optional[float] = None
    imageUrl: str
    category: str
    description: Optional[str] = None
    rating: Optional[float] = None
    discount: Optional[float] = None
    brand: Optional[str] = None  # Add brand field
    tags: Optional[List[str]] = None  # Add tags field
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def as_text(self) -> str:
        """Convert product to text representation for embeddings"""
        # Use title if available, otherwise use name
        title = self.title or self.name
        
        # Build comprehensive text representation
        parts = [title]
        
        if self.brand:
            parts.append(f"Brand: {self.brand}")
        
        if self.category:
            parts.append(f"Category: {self.category}")
        
        if self.description:
            parts.append(f"Description: {self.description}")
        
        if self.tags:
            parts.append(f"Tags: {', '.join(self.tags)}")
        
        parts.append(f"Price: {self.price}")
        
        return " | ".join(parts)

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

# Wishlist Recommendation Models
class WishlistRecommendationRequest(BaseModel):
    product_ids: List[int]
    user_id: Optional[str] = None  # User ID to exclude their shared wishlists

class ProductSuggestion(BaseModel):
    id: int
    name: str
    price: float
    original_price: Optional[float] = None
    category: str
    imageUrl: str
    description: Optional[str] = None
    rating: Optional[float] = None
    discount: Optional[float] = None

class WishlistRecommendation(BaseModel):
    query: str
    product_query_id: int
    suggestion: str
    product_suggestion: ProductSuggestion

class WishlistRecommendationResponse(BaseModel):
    status: str
    recommendations: List[WishlistRecommendation]
    total_recommendations: int
