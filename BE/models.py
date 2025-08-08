from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Product(BaseModel):
    id: Optional[int] = None
    name: str
    price: float
    original_price: Optional[float] = None
    image: str
    category: str
    description: Optional[str] = None
    brand: Optional[str] = None
    tags: Optional[List[str]] = []
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
    image: str
    category: str
    description: Optional[str] = None
    brand: Optional[str] = None
    tags: Optional[List[str]] = []
    color: Optional[str] = None
    size: Optional[str] = None
    rating: Optional[float] = None
    is_new: Optional[bool] = False
    discount: Optional[float] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    image: Optional[str] = None
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
