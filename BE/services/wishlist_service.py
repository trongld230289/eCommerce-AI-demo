import time
from typing import List, Optional
from firebase_config import get_firestore_db
from models import Wishlist, WishlistCreate, WishlistUpdate, WishlistItem
from product_service import product_service

class WishlistService:
    def __init__(self):
        self.db = get_firestore_db()
        self.collection_name = 'wishlists'

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
                          .order_by("created_at")\
                          .stream()
            
            wishlists = []
            for doc in docs:
                data = doc.to_dict()
                if data:
                    wishlists.append(Wishlist(**data))
            
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
                    raise Exception("Product already in wishlist")
            
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
            return Wishlist(**updated_doc.to_dict())
            
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
            
            # Return updated wishlist
            updated_doc = doc_ref.get()
            return Wishlist(**updated_doc.to_dict())
            
        except Exception as e:
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
