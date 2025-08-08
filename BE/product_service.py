from typing import List, Optional, Dict, Any
from firebase_config import get_firestore_db
from models import Product, ProductCreate, ProductUpdate, SearchFilters
from google.cloud.firestore_v1.base_query import FieldFilter
import time

class ProductService:
    def __init__(self):
        self.db = get_firestore_db()
        self.collection_name = 'products'
        # Mock data for development when Firebase is not available
        self.mock_products = [
            {
                "id": 1,
                "name": "Wireless Bluetooth Headphones",
                "description": "High-quality wireless headphones with noise cancellation",
                "price": 99.99,
                "category": "Electronics",
                "brand": "AudioTech",
                "imageUrl": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
                "stock": 50,
                "rating": 4.5,
                "featured": True,
                "created_at": time.time(),
                "updated_at": time.time()
            },
            {
                "id": 2,
                "name": "Smart Fitness Watch",
                "description": "Track your fitness goals with this advanced smartwatch",
                "price": 299.99,
                "category": "Electronics",
                "brand": "FitTech",
                "imageUrl": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500",
                "stock": 30,
                "rating": 4.7,
                "featured": True,
                "created_at": time.time(),
                "updated_at": time.time()
            },
            {
                "id": 3,
                "name": "Portable Laptop Stand",
                "description": "Ergonomic adjustable laptop stand for better posture",
                "price": 49.99,
                "category": "Accessories",
                "brand": "ErgoDesk",
                "imageUrl": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500",
                "stock": 75,
                "rating": 4.3,
                "featured": False,
                "created_at": time.time(),
                "updated_at": time.time()
            }
        ]
    
    def _use_mock_data(self):
        """Check if we should use mock data (when Firebase is not available)"""
        return self.db is None
    
    def create_product(self, product_data: ProductCreate) -> Dict[str, Any]:
        """Create a new product"""
        try:
            # Get next available ID
            next_id = self._get_next_product_id()
            
            # Convert to dict and add ID and timestamps
            product_dict = product_data.dict()
            product_dict['id'] = next_id
            product_dict['created_at'] = time.time()
            product_dict['updated_at'] = time.time()
            
            # Add to Firestore
            doc_ref = self.db.collection(self.collection_name).document(str(next_id))
            doc_ref.set(product_dict)
            
            return {"success": True, "product_id": next_id, "data": product_dict}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product by ID"""
        try:
            if self._use_mock_data():
                # Find product in mock data
                for product in self.mock_products:
                    if product['id'] == product_id:
                        return product.copy()
                return None
            
            doc_ref = self.db.collection(self.collection_name).document(str(product_id))
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting product {product_id}: {e}")
            # Fallback to mock data
            for product in self.mock_products:
                if product['id'] == product_id:
                    return product.copy()
            return None
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products"""
        try:
            if self._use_mock_data():
                print("📝 Using mock data (Firebase not available)")
                return self.mock_products.copy()
            
            docs = self.db.collection(self.collection_name).stream()
            products = []
            
            for doc in docs:
                product_data = doc.to_dict()
                products.append(product_data)
            
            # Sort by ID
            products.sort(key=lambda x: x.get('id', 0))
            return products
        except Exception as e:
            print(f"Error getting all products: {e}")
            print("📝 Falling back to mock data")
            return self.mock_products.copy()
    
    def update_product(self, product_id: int, product_data: ProductUpdate) -> Dict[str, Any]:
        """Update product"""
        try:
            doc_ref = self.db.collection(self.collection_name).document(str(product_id))
            
            # Check if product exists
            if not doc_ref.get().exists:
                return {"success": False, "error": "Product not found"}
            
            # Update data
            update_data = {k: v for k, v in product_data.dict().items() if v is not None}
            update_data['updated_at'] = time.time()
            
            doc_ref.update(update_data)
            
            # Get updated product
            updated_product = doc_ref.get().to_dict()
            return {"success": True, "data": updated_product}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_product(self, product_id: int) -> Dict[str, Any]:
        """Delete product"""
        try:
            doc_ref = self.db.collection(self.collection_name).document(str(product_id))
            
            # Check if product exists
            if not doc_ref.get().exists:
                return {"success": False, "error": "Product not found"}
            
            doc_ref.delete()
            return {"success": True, "message": "Product deleted successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_products(self, filters: SearchFilters) -> List[Dict[str, Any]]:
        """Search products with filters"""
        try:
            query = self.db.collection(self.collection_name)
            
            # Apply filters
            if filters.category and filters.category.lower() != 'all':
                query = query.where(filter=FieldFilter("category", "==", filters.category))
            
            if filters.brand and filters.brand.lower() != 'all':
                query = query.where(filter=FieldFilter("brand", "==", filters.brand))
            
            if filters.min_price:
                query = query.where(filter=FieldFilter("price", ">=", filters.min_price))
            
            if filters.max_price:
                query = query.where(filter=FieldFilter("price", "<=", filters.max_price))
            
            # Get results
            docs = query.stream()
            products = []
            
            for doc in docs:
                product_data = doc.to_dict()
                
                # Apply keyword search on client side (Firestore doesn't support full-text search)
                if filters.keywords:
                    keywords = filters.keywords.lower().split(',')
                    keywords = [kw.strip() for kw in keywords if kw.strip()]
                    
                    # Check if any keyword matches name, description, or tags
                    product_text = f"{product_data.get('name', '')} {product_data.get('description', '')}".lower()
                    product_tags = [tag.lower() for tag in product_data.get('tags', [])]
                    
                    keyword_match = False
                    for keyword in keywords:
                        if (keyword in product_text or 
                            any(keyword in tag for tag in product_tags)):
                            keyword_match = True
                            break
                    
                    if not keyword_match:
                        continue
                
                products.append(product_data)
            
            # Sort by ID
            products.sort(key=lambda x: x.get('id', 0))
            return products
        except Exception as e:
            print(f"Error searching products: {e}")
            return []
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        try:
            docs = self.db.collection(self.collection_name).stream()
            categories = set()
            
            for doc in docs:
                product_data = doc.to_dict()
                category = product_data.get('category')
                if category:
                    categories.add(category)
            
            return sorted(list(categories))
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    def get_brands(self) -> List[str]:
        """Get all unique brands"""
        try:
            docs = self.db.collection(self.collection_name).stream()
            brands = set()
            
            for doc in docs:
                product_data = doc.to_dict()
                brand = product_data.get('brand')
                if brand:
                    brands.add(brand)
            
            return sorted(list(brands))
        except Exception as e:
            print(f"Error getting brands: {e}")
            return []
    
    def _get_next_product_id(self) -> int:
        """Get next available product ID"""
        try:
            docs = self.db.collection(self.collection_name).stream()
            max_id = 0
            
            for doc in docs:
                product_data = doc.to_dict()
                product_id = product_data.get('id', 0)
                if product_id > max_id:
                    max_id = product_id
            
            return max_id + 1
        except Exception as e:
            print(f"Error getting next product ID: {e}")
            return 1

# Global service instance
product_service = ProductService()
