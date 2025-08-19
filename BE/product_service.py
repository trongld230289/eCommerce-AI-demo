from typing import List, Optional, Dict, Any
from firebase_config import get_firestore_db
from models import Product, ProductCreate, ProductUpdate, SearchFilters
from google.cloud.firestore_v1.base_query import FieldFilter
import time
import threading
from datetime import datetime, timedelta

class ProductService:
    def __init__(self):
        self.db = get_firestore_db()
        self.collection_name = 'products'
        
        # Cache management
        self._cache = {}
        self._cache_expiry = {}
        self._cache_lock = threading.Lock()
        self.cache_duration = 300  # 5 minutes
        
        if self.db is None:
            raise ConnectionError("Firebase connection failed. Please check your configuration.")
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache is still valid"""
        return (key in self._cache and 
                key in self._cache_expiry and 
                datetime.now() < self._cache_expiry[key])
    
    def _set_cache(self, key: str, data: Any) -> None:
        """Set cache with expiry"""
        with self._cache_lock:
            self._cache[key] = data
            self._cache_expiry[key] = datetime.now() + timedelta(seconds=self.cache_duration)
    
    def _get_cache(self, key: str) -> Optional[Any]:
        """Get from cache if valid"""
        with self._cache_lock:
            if self._is_cache_valid(key):
                return self._cache[key]
            # Clean expired cache
            if key in self._cache:
                del self._cache[key]
                del self._cache_expiry[key]
            return None
    
    def _clear_products_cache(self) -> None:
        """Clear products-related cache"""
        with self._cache_lock:
            keys_to_remove = [k for k in self._cache.keys() if k.startswith('products_')]
            for key in keys_to_remove:
                del self._cache[key]
                del self._cache_expiry[key]
    
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
            
            # Write latest categories to JSON file
            self._dump_categories_to_json()
            return {"success": True, "product_id": next_id, "data": product_dict}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get product by ID"""
        try:
            doc_ref = self.db.collection(self.collection_name).document(str(product_id))
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting product {product_id}: {e}")
            return None
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products"""
        try:
            docs = self.db.collection(self.collection_name).get()
            products = []
            
            for doc in docs:
                product_data = doc.to_dict()
                products.append(product_data)
            
            # Sort by ID
            products.sort(key=lambda x: x.get('id', 0))
            return products
        except Exception as e:
            print(f"Error getting all products: {e}")
            return []
    
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
            # Write latest categories to JSON file
            self._dump_categories_to_json()
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
            # Write latest categories to JSON file
            self._dump_categories_to_json()
            return {"success": True, "message": "Product deleted successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    def _dump_categories_to_json(self, generate_keywords: bool = True):
        """Write latest categories to a JSON file and optionally generate category keywords"""
        try:
            import json
            categories = self.get_categories()
            
            # Save categories to file
            with open("latest_categories.json", "w", encoding="utf-8") as f:
                json.dump(categories, f, ensure_ascii=False, indent=2)
            print(f"✅ Categories saved to latest_categories.json: {categories}")
            
            # Generate category keywords using AI service
            if generate_keywords and categories:
                try:
                    # Import here to avoid circular imports
                    from services.ai_service import AIService
                    
                    print("🤖 Generating category keywords using LLM...")
                    ai_service = AIService()
                    
                    # Use the new combined method that generates and saves in one call
                    success = ai_service.generate_and_save_category_keywords(categories)
                    
                    if success:
                        print(f"✅ Successfully generated and saved keywords for categories")
                    else:
                        print("⚠️ Failed to generate or save category keywords")
                        
                except Exception as e:
                    print(f"⚠️ Error generating category keywords: {str(e)}")
                    # Don't fail the whole operation if keyword generation fails
            
        except Exception as e:
            print(f"❌ Error dumping categories to JSON: {e}")
    
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
            docs = query.get()
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
            docs = self.db.collection(self.collection_name).get()
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
            docs = self.db.collection(self.collection_name).get()
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
            docs = self.db.collection(self.collection_name).get()
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
