from pydantic import BaseModel
from typing import List, Optional

class Product(BaseModel):
    id: int
    name: str
    price: float
    original_price: Optional[float] = None
    image: str
    category: str
    description: str
    brand: str
    tags: List[str] = []
    color: Optional[str] = None
    rating: float
    isNew: bool = False
    discount: float = 0

class RecommendationResponse(BaseModel):
    products: List[Product]
    is_personalized: bool
    user_id: Optional[str] = None
