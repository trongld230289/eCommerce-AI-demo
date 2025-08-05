from pydantic import BaseModel
from typing import List, Optional

class Product(BaseModel):
    id: str
    name: str
    description: str
    price: int
    image: str
    category: str
    brand: str
    inStock: bool
    stock: int
    rating: float
    reviews: int

class RecommendationResponse(BaseModel):
    products: List[Product]
    is_personalized: bool
    user_id: Optional[str] = None
