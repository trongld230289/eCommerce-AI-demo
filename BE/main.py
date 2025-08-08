from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from models import Product, ProductCreate, ProductUpdate, SearchFilters, ApiResponse
from product_service import product_service
import uvicorn

app = FastAPI(
    title="eCommerce Backend API",
    description="Backend API for eCommerce application with Firebase integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "eCommerce Backend API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

# Product endpoints
@app.get("/products", response_model=List[dict])
async def get_products():
    """Get all products"""
    try:
        products = product_service.get_all_products()
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving products: {str(e)}")

@app.get("/products/{product_id}")
async def get_product(product_id: int):
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

@app.post("/products")
async def create_product(product: ProductCreate):
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

@app.put("/products/{product_id}")
async def update_product(product_id: int, product: ProductUpdate):
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

@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
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

# Search endpoint
@app.get("/search")
async def search_products(
    category: Optional[str] = Query(None, description="Product category"),
    brand: Optional[str] = Query(None, description="Product brand"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    keywords: Optional[str] = Query(None, description="Keywords (comma-separated)")
):
    """Search products with filters"""
    try:
        filters = SearchFilters(
            category=category,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            keywords=keywords
        )
        products = product_service.search_products(filters)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching products: {str(e)}")

# Category and brand endpoints
@app.get("/categories")
async def get_categories():
    """Get all product categories"""
    try:
        categories = product_service.get_categories()
        return {"categories": ["All"] + categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving categories: {str(e)}")

@app.get("/brands")
async def get_brands():
    """Get all product brands"""
    try:
        brands = product_service.get_brands()
        return {"brands": ["All"] + brands}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving brands: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
