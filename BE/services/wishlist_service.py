import time
from typing import List, Optional
from firebase_config import get_firestore_db
from models import Wishlist, WishlistCreate, WishlistUpdate, WishlistItem
from product_service import product_service

class WishlistService:
    def __init__(self):
        self.db = get_firestore_db()
        self.collection_name = 'wishlists'

    def _populate_product_details(self, wishlist_data: dict) -> dict:
        """Populate product details for wishlist items"""
        try:
            if 'products' in wishlist_data and wishlist_data['products']:
                populated_products = []
                for item in wishlist_data['products']:
                    product_id = item.get('product_id')
                    if product_id:
                        # Get product details from product service
                        product_details = product_service.get_product_by_id(product_id)
                        if product_details:
                            # Combine wishlist item data with product details
                            populated_item = {
                                'product_id': product_id,
                                'added_at': item.get('added_at'),
                                'product_details': product_details
                            }
                            populated_products.append(populated_item)
                        else:
                            # Keep original item if product not found
                            populated_products.append(item)
                    else:
                        populated_products.append(item)
                
                wishlist_data['products'] = populated_products
            
            return wishlist_data
        except Exception as e:
            print(f"Warning: Error populating product details: {e}")
            return wishlist_data

    def create_default_wishlists(self, user_id: str) -> List[Wishlist]:
        """Create default wishlists for a new user"""
        default_wishlists = [
            {"name": "My Favorites ❤️", "user_id": user_id},
            {"name": "Gift Ideas 🎁", "user_id": user_id}
        ]
        
        created_wishlists = []
        for wishlist_data in default_wishlists:
            wishlist = self.create_wishlist(WishlistCreate(**wishlist_data))
            created_wishlists.append(wishlist)
        
        return created_wishlists

    def create_wishlist(self, wishlist_data: WishlistCreate) -> Wishlist:
        """Create a new wishlist"""
        try:
            # Generate new document reference
            doc_ref = self.db.collection(self.collection_name).document()
            
            wishlist_dict = {
                "id": doc_ref.id,
                "user_id": wishlist_data.user_id,
                "name": wishlist_data.name,
                "products": [],
                "item_count": 0,
                "created_at": time.time(),
                "updated_at": time.time()
            }
            
            doc_ref.set(wishlist_dict)
            return Wishlist(**wishlist_dict)
            
        except Exception as e:
            raise Exception(f"Error creating wishlist: {str(e)}")

    def get_user_wishlists(self, user_id: str) -> List[Wishlist]:
        """Get all wishlists for a user"""
        try:
            docs = self.db.collection(self.collection_name)\
                          .where("user_id", "==", user_id)\
                          .stream()
            
            wishlists = []
            for doc in docs:
                data = doc.to_dict()
                if data:
                    # Ensure the document has an id
                    if 'id' not in data:
                        data['id'] = doc.id
                    
                    # Convert Firestore timestamps to float
                    if 'created_at' in data:
                        if hasattr(data['created_at'], 'timestamp'):
                            data['created_at'] = data['created_at'].timestamp()
                        elif not isinstance(data['created_at'], (int, float)):
                            data['created_at'] = time.time()
                    else:
                        data['created_at'] = time.time()
                    
                    if 'updated_at' in data:
                        if hasattr(data['updated_at'], 'timestamp'):
                            data['updated_at'] = data['updated_at'].timestamp()
                        elif not isinstance(data['updated_at'], (int, float)):
                            data['updated_at'] = time.time()
                    else:
                        data['updated_at'] = time.time()
                    
                    # Ensure products is a list
                    if 'products' not in data:
                        data['products'] = []
                    
                    # Ensure item_count exists
                    if 'item_count' not in data:
                        data['item_count'] = len(data.get('products', []))
                    
                    # Populate product details for wishlist items
                    data = self._populate_product_details(data)
                    
                    wishlists.append(Wishlist(**data))
            
            # Sort by created_at in Python instead of Firestore
            wishlists.sort(key=lambda x: x.created_at)
            
            # Create default wishlists if user has none
            if not wishlists:
                wishlists = self.create_default_wishlists(user_id)
            
            return wishlists
            
        except Exception as e:
            raise Exception(f"Error fetching wishlists: {str(e)}")

    def get_wishlist(self, wishlist_id: str, user_id: str) -> Optional[Wishlist]:
        """Get a specific wishlist by ID"""
        try:
            doc_ref = self.db.collection(self.collection_name).document(wishlist_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
                
            data = doc.to_dict()
            if data and data.get("user_id") == user_id:
                # Ensure the document has an id
                if 'id' not in data:
                    data['id'] = doc.id
                
                # Convert Firestore timestamps to float
                if 'created_at' in data and hasattr(data['created_at'], 'timestamp'):
                    data['created_at'] = data['created_at'].timestamp()
                if 'updated_at' in data and hasattr(data['updated_at'], 'timestamp'):
                    data['updated_at'] = data['updated_at'].timestamp()
                
                return Wishlist(**data)
            
            return None
            
        except Exception as e:
            raise Exception(f"Error fetching wishlist: {str(e)}")

    def update_wishlist(self, wishlist_id: str, user_id: str, update_data: WishlistUpdate) -> Optional[Wishlist]:
        """Update wishlist name"""
        try:
            doc_ref = self.db.collection(self.collection_name).document(wishlist_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
                
            data = doc.to_dict()
            if not data or data.get("user_id") != user_id:
                return None
            
            update_dict = {"updated_at": time.time()}
            if update_data.name is not None:
                update_dict["name"] = update_data.name
            
            doc_ref.update(update_dict)
            
            # Return updated wishlist
            updated_doc = doc_ref.get()
            return Wishlist(**updated_doc.to_dict())
            
        except Exception as e:
            raise Exception(f"Error updating wishlist: {str(e)}")

    def delete_wishlist(self, wishlist_id: str, user_id: str) -> bool:
        """Delete a wishlist"""
        try:
            doc_ref = self.db.collection(self.collection_name).document(wishlist_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False
                
            data = doc.to_dict()
            if not data or data.get("user_id") != user_id:
                return False
            
            doc_ref.delete()
            return True
            
        except Exception as e:
            raise Exception(f"Error deleting wishlist: {str(e)}")

    def add_product_to_wishlist(self, wishlist_id: str, user_id: str, product_id: int) -> Optional[Wishlist]:
        """Add a product to wishlist"""
        try:
            # Verify product exists
            product = product_service.get_product_by_id(product_id)
            if not product:
                raise Exception("Product not found")
            
            doc_ref = self.db.collection(self.collection_name).document(wishlist_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
                
            data = doc.to_dict()
            if not data or data.get("user_id") != user_id:
                return None
            
            # Check if product already in wishlist
            products = data.get("products", [])
            for item in products:
                if item.get("product_id") == product_id:
                    # Product already exists, return current wishlist instead of raising error
                    # Ensure the document has an id
                    if 'id' not in data:
                        data['id'] = doc.id
                    
                    # Convert Firestore timestamps to float if needed
                    if 'created_at' in data and hasattr(data['created_at'], 'timestamp'):
                        data['created_at'] = data['created_at'].timestamp()
                    if 'updated_at' in data and hasattr(data['updated_at'], 'timestamp'):
                        data['updated_at'] = data['updated_at'].timestamp()
                    
                    return Wishlist(**data)
            
            # Add product
            new_item = {
                "product_id": product_id,
                "added_at": time.time()
            }
            products.append(new_item)
            
            update_dict = {
                "products": products,
                "item_count": len(products),
                "updated_at": time.time()
            }
            
            doc_ref.update(update_dict)
            
            # Return updated wishlist
            updated_doc = doc_ref.get()
            updated_data = updated_doc.to_dict()
            
            # Ensure the document has an id
            if 'id' not in updated_data:
                updated_data['id'] = updated_doc.id
            
            # Convert Firestore timestamps to float if needed
            if 'created_at' in updated_data and hasattr(updated_data['created_at'], 'timestamp'):
                updated_data['created_at'] = updated_data['created_at'].timestamp()
            if 'updated_at' in updated_data and hasattr(updated_data['updated_at'], 'timestamp'):
                updated_data['updated_at'] = updated_data['updated_at'].timestamp()
            
            return Wishlist(**updated_data)
            
        except Exception as e:
            raise Exception(f"Error adding product to wishlist: {str(e)}")

    def remove_product_from_wishlist(self, wishlist_id: str, user_id: str, product_id: int) -> Optional[Wishlist]:
        """Remove a product from wishlist"""
        try:
            doc_ref = self.db.collection(self.collection_name).document(wishlist_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
                
            data = doc.to_dict()
            if not data or data.get("user_id") != user_id:
                return None
            
            # Remove product
            products = data.get("products", [])
            products = [item for item in products if item.get("product_id") != product_id]
            
            update_dict = {
                "products": products,
                "item_count": len(products),
                "updated_at": time.time()
            }
            
            doc_ref.update(update_dict)
            
            # Return updated wishlist with populated product details
            updated_doc = doc_ref.get()
            updated_data = updated_doc.to_dict()
            
            # Ensure the document has an id
            if 'id' not in updated_data:
                updated_data['id'] = updated_doc.id
            
            # Convert Firestore timestamps to float
            if 'created_at' in updated_data:
                if hasattr(updated_data['created_at'], 'timestamp'):
                    updated_data['created_at'] = updated_data['created_at'].timestamp()
                elif not isinstance(updated_data['created_at'], (int, float)):
                    updated_data['created_at'] = time.time()
            
            if 'updated_at' in updated_data:
                if hasattr(updated_data['updated_at'], 'timestamp'):
                    updated_data['updated_at'] = updated_data['updated_at'].timestamp()
                elif not isinstance(updated_data['updated_at'], (int, float)):
                    updated_data['updated_at'] = time.time()
            
            # Populate product details
            updated_data = self._populate_product_details(updated_data)
            
            # Convert to Pydantic model safely by ensuring products structure is correct
            wishlist_dict = {
                "id": updated_data["id"],
                "user_id": updated_data["user_id"],
                "name": updated_data["name"],
                "products": updated_data.get("products", []),
                "item_count": updated_data.get("item_count", 0),
                "created_at": updated_data["created_at"],
                "updated_at": updated_data["updated_at"]
            }
            
            return Wishlist(**wishlist_dict)
            
        except Exception as e:
            print(f"Error removing product from wishlist: {str(e)}")
            raise Exception(f"Error removing product from wishlist: {str(e)}")

    def clear_wishlist(self, wishlist_id: str, user_id: str) -> Optional[Wishlist]:
        """Clear all products from wishlist"""
        try:
            doc_ref = self.db.collection(self.collection_name).document(wishlist_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
                
            data = doc.to_dict()
            if not data or data.get("user_id") != user_id:
                return None
            
            update_dict = {
                "products": [],
                "item_count": 0,
                "updated_at": time.time()
            }
            
            doc_ref.update(update_dict)
            
            # Return updated wishlist
            updated_doc = doc_ref.get()
            return Wishlist(**updated_doc.to_dict())
            
        except Exception as e:
            raise Exception(f"Error clearing wishlist: {str(e)}")

# Create global instance
wishlist_service = WishlistService()
