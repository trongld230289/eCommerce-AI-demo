from fastapi import APIRouter, HTTPException
from typing import List
from models import Product, ProductCreate, ProductUpdate, SearchFilters, ApiResponse
from product_service import product_service

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[Product])
def get_all_products():
    """Get all products"""
    try:
        products = product_service.get_all_products()
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving products: {str(e)}")

@router.get("/{product_id}")
def get_product(product_id: int):
    """Get product by ID"""
    try:
        product = product_service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving product: {str(e)}")

@router.post("/")
def create_product(product: ProductCreate):
    """Create a new product"""
    try:
        result = product_service.create_product(product)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create product"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")

@router.put("/{product_id}")
def update_product(product_id: int, product: ProductUpdate):
    """Update a product"""
    try:
        result = product_service.update_product(product_id, product)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to update product"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating product: {str(e)}")

@router.delete("/{product_id}")
def delete_product(product_id: int):
    """Delete a product"""
    try:
        result = product_service.delete_product(product_id)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to delete product"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting product: {str(e)}")

@router.get("/search/", response_model=List[Product])
def search_products(
    query: str = "",
    category: str = "",
    min_price: float = None,
    max_price: float = None,
    brand: str = ""
):
    """Search products with filters"""
    try:
        filters = SearchFilters(
            query=query,
            category=category,
            min_price=min_price,
            max_price=max_price,
            brand=brand
        )
        products = product_service.search_products(filters)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching products: {str(e)}")
