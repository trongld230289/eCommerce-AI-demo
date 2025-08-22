import time
from typing import List, Optional
import httpx
from fastapi import HTTPException
from firebase_config import get_firestore_db
from models import (
    Wishlist, WishlistCreate, WishlistUpdate, WishlistItem, ShareType, 
    WishlistShareUpdate, WishlistShareResponse, WishlistSearchResult, 
    WishlistSearchResponse
)
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

    def create_default_wishlists(self, user_id: str, user_email: str = None, user_name: str = None) -> List[Wishlist]:
        """Create default wishlists for a new user"""
        default_wishlists = [
            {"name": "My Favorites ❤️", "user_id": user_id, "user_email": user_email, "user_name": user_name},
            {"name": "Gift Ideas 🎁", "user_id": user_id, "user_email": user_email, "user_name": user_name}
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
            
            # Debug logging
            print(f"Creating wishlist with data:")
            print(f"  user_id: {wishlist_data.user_id}")
            print(f"  user_email: {wishlist_data.user_email}")
            print(f"  user_name: {wishlist_data.user_name}")
            print(f"  name: {wishlist_data.name}")
            
            # Force populate user info from Firebase Auth if null
            user_email = wishlist_data.user_email
            user_name = wishlist_data.user_name
            
            if not user_email or not user_name:
                try:
                    from firebase_admin import auth as firebase_auth
                    print(f"SERVICE: user_email or user_name is null, fetching from Firebase Auth...")
                    user_record = firebase_auth.get_user(wishlist_data.user_id)
                    user_email = user_record.email or user_email
                    user_name = user_record.display_name or (user_record.email.split('@')[0] if user_record.email else user_name)
                    print(f"SERVICE: Got user info from Firebase Auth:")
                    print(f"  user_email: {user_email}")
                    print(f"  user_name: {user_name}")
                except Exception as e:
                    print(f"SERVICE: Could not get user info from Firebase Auth: {e}")
            
            wishlist_dict = {
                "id": doc_ref.id,
                "user_id": wishlist_data.user_id,
                "user_email": user_email,
                "user_name": user_name,
                "name": wishlist_data.name,
                "products": [],
                "item_count": 0,
                "share_status": ShareType.PRIVATE.value,  # Default to private
                "created_at": time.time(),
                "updated_at": time.time()
            }
            
            print(f"Saving wishlist to Firestore with dict: {wishlist_dict}")
            doc_ref.set(wishlist_dict)

             # thangnaozay
             # Thuong implementation - create the wishlist
            with httpx.Client() as client:
                neo_data = {
                    "id": wishlist_dict["id"],
                    "name": wishlist_dict["name"],
                    "user_id": wishlist_dict["user_id"],
                    "note": None,  # Assuming note is not provided in WishlistCreate
                }
                response = client.post("http://localhost:8003/api/wishlist", json=neo_data)
                if response.status_code != 200:
                    raise HTTPException(status_code=500, detail=f"Failed to sync create with external service: {response.text}")
            # ...existing code...
            return Wishlist(**wishlist_dict)
            
        except Exception as e:
            raise Exception(f"Error creating wishlist: {str(e)}")

    def get_user_wishlists(self, user_id: str, user_email: str = None, user_name: str = None) -> List[Wishlist]:
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

            # Thuong implementation - update the wishlist
            with httpx.Client() as client:
                response = client.put(
                    f"http://localhost:8003/api/wishlist/{wishlist_id}",
                    params={"user_id": user_id},
                    json=update_data.dict(exclude_unset=True)
                )
                if response.status_code != 200:
                    raise HTTPException(status_code=500, detail=f"Failed to sync update with external service: {response.text}")

            
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

            print(f"Wishlist '{wishlist_id}' deleted successfully")
            # Thuong implementation - delete wishlist
            with httpx.Client() as client:
                try:
                    response = client.delete(
                        f"http://localhost:8003/api/wishlist/{wishlist_id}",
                        params={"user_id": user_id},
                        timeout=5.0
                    )
                    if response.status_code != 200:
                        print(f"Warning: Failed to sync delete with external service: {response.text}")
                except Exception as sync_error:
                    print(f"Warning: External sync failed (service may be down): {sync_error}")
                    
            return True
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting wishlist: {str(e)}")

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

            with httpx.Client() as client:
                try:
                    response = client.post(
                        f"http://localhost:8003/api/wishlist/{wishlist_id}/products",
                        params={"user_id": user_id},
                        json=new_item,
                        timeout=5.0
                    )
                    print(f"DEBUG BE ROUTER: Neo4j service response - status: {response.status_code}, text: {response.text[:200]}")
                    if response.status_code != 200:
                        print(f"Warning: Failed to sync add product with external service: {response.text}")
                except Exception as sync_error:
                    print(f"Warning: External sync failed (service may be down): {sync_error}")
                
            return Wishlist(**updated_data)
            
        except Exception as e:
            raise Exception(f"Error adding product to wishlist: {str(e)}")

    def add_product_to_shared_wishlist(self, shared_wishlist_id: str, product_id: int, target_wishlist_id: str, user_id: str) -> bool:
        """Add a product from a shared wishlist to user's own wishlist"""
        try:
            # First, verify the shared wishlist exists and is actually shared
            shared_doc_ref = self.db.collection(self.collection_name).document(shared_wishlist_id)
            shared_doc = shared_doc_ref.get()
            
            if not shared_doc.exists:
                return False
            
            shared_data = shared_doc.to_dict()
            if not shared_data:
                return False
            
            # Check if the wishlist is publicly shared
            share_status = shared_data.get("share_status", ShareType.PRIVATE.value)
            if share_status not in [ShareType.PUBLIC.value, ShareType.ANONYMOUS.value]:
                return False
            
            # Verify the product exists in the shared wishlist
            shared_products = shared_data.get("products", [])
            product_found = False
            for item in shared_products:
                if item.get("product_id") == product_id:
                    product_found = True
                    break
            
            if not product_found:
                return False
            
            # Now add the product to the user's target wishlist
            target_doc_ref = self.db.collection(self.collection_name).document(target_wishlist_id)
            target_doc = target_doc_ref.get()
            
            if not target_doc.exists:
                return False
                
            target_data = target_doc.to_dict()
            if not target_data or target_data.get("user_id") != user_id:
                return False
            
            # Check if product already in target wishlist
            target_products = target_data.get("products", [])
            for item in target_products:
                if item.get("product_id") == product_id:
                    # Product already exists, return True (success)
                    return True
            
            # Add product to target wishlist
            new_item = {
                "product_id": product_id,
                "added_at": time.time()
            }
            target_products.append(new_item)
            
            update_dict = {
                "products": target_products,
                "item_count": len(target_products),
                "updated_at": time.time()
            }
            
            target_doc_ref.update(update_dict)
            return True
            
        except Exception as e:
            print(f"Error adding product from shared wishlist: {str(e)}")
            return False

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

            # Thuong implementation - remove product from wishlist
            with httpx.Client() as client:
                try:
                    response = client.delete(
                        f"http://localhost:8003/api/wishlist/{wishlist_id}/products/{product_id}",
                        params={"user_id": user_id},
                        timeout=5.0
                    )
                    if response.status_code != 200:
                        print(f"Warning: Failed to sync remove product with external service: {response.text}")
                except Exception as sync_error:
                    print(f"Warning: External sync failed (service may be down): {sync_error}")
            
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

            with httpx.Client() as client:
                try:
                    response = client.post(
                        f"http://localhost:8003/api/wishlist/{wishlist_id}/clear",
                        params={"user_id": user_id},
                        timeout=5.0
                    )
                    if response.status_code != 200:
                        print(f"Warning: Failed to sync clear with external service: {response.text}")
                except Exception as sync_error:
                    print(f"Warning: External sync failed (service may be down): {sync_error}")
            
            # Return updated wishlist
            updated_doc = doc_ref.get()
            return Wishlist(**updated_doc.to_dict())
            
        except Exception as e:
            raise Exception(f"Error clearing wishlist: {str(e)}")

    def update_share_status(self, wishlist_id: str, user_id: str, share_update: WishlistShareUpdate) -> WishlistShareResponse:
        """Update wishlist share status"""
        try:
            doc_ref = self.db.collection(self.collection_name).document(wishlist_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return WishlistShareResponse(
                    success=False,
                    message="Wishlist not found",
                    share_status=ShareType.PRIVATE
                )
            
            data = doc.to_dict()
            if data['user_id'] != user_id:
                return WishlistShareResponse(
                    success=False,
                    message="Unauthorized access to wishlist",
                    share_status=ShareType.PRIVATE
                )
            
            # Update share status
            update_dict = {
                "share_status": share_update.share_status.value,
                "updated_at": time.time()
            }
            
            doc_ref.update(update_dict)
            
            # Generate share URL if not private
            share_url = None
            if share_update.share_status != ShareType.PRIVATE:
                base_url = "http://localhost:3000"  # This should be configurable
                share_url = f"{base_url}/shared-wishlist/{wishlist_id}"
            
            success_messages = {
                ShareType.PUBLIC: f"Wishlist '{data['name']}' is now public! Anyone with the link can view it.",
                ShareType.ANONYMOUS: f"Wishlist '{data['name']}' is now shared anonymously! Anyone with the link can view it without seeing your name.",
                ShareType.PRIVATE: f"Wishlist '{data['name']}' is now private."
            }
            
            return WishlistShareResponse(
                success=True,
                message=success_messages[share_update.share_status],
                share_status=share_update.share_status,
                share_url=share_url
            )
            
        except Exception as e:
            return WishlistShareResponse(
                success=False,
                message=f"Error updating share status: {str(e)}",
                share_status=ShareType.PRIVATE
            )

    def get_shared_wishlist(self, wishlist_id: str) -> Optional[Wishlist]:
        """Get a shared wishlist by ID (public access)"""
        try:
            doc_ref = self.db.collection(self.collection_name).document(wishlist_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            data = doc.to_dict()
            
            # Only return if wishlist is shared (not private)
            if data.get('share_status', ShareType.PRIVATE.value) == ShareType.PRIVATE.value:
                return None
            
            # If anonymous sharing, remove user identification
            if data.get('share_status') == ShareType.ANONYMOUS.value:
                data['user_id'] = "anonymous"
            
            # Populate product details
            data = self._populate_product_details(data)
            
            return Wishlist(**data)
            
        except Exception as e:
            print(f"Error fetching shared wishlist: {str(e)}")
            return None

    def search_wishlists_by_email(self, email: str) -> WishlistSearchResponse:
        """Search for shared wishlists by user email"""
        try:
            # Query wishlists where user_email matches and share_status is not private
            docs = self.db.collection(self.collection_name)\
                          .where("user_email", "==", email)\
                          .where("share_status", "in", [ShareType.PUBLIC.value, ShareType.ANONYMOUS.value])\
                          .stream()
            
            search_results = []
            for doc in docs:
                data = doc.to_dict()
                if data:
                    # Create search result
                    result = WishlistSearchResult(
                        id=data.get("id", doc.id),
                        user_id=data.get("user_id", ""),
                        user_email=data.get("user_email", email),
                        user_name=data.get("user_name", ""),
                        name=data.get("name", ""),
                        item_count=data.get("item_count", 0),
                        share_status=ShareType(data.get("share_status", ShareType.PRIVATE.value)),
                        created_at=data.get("created_at", 0),
                        updated_at=data.get("updated_at", 0)
                    )
                    
                    # If anonymous sharing, hide user identification
                    if result.share_status == ShareType.ANONYMOUS:
                        result.user_id = "anonymous"
                        result.user_email = "anonymous@example.com"
                        result.user_name = "Anonymous User"
                    
                    search_results.append(result)
            
            return WishlistSearchResponse(
                success=True,
                message=f"Found {len(search_results)} shared wishlists for {email}",
                wishlists=search_results
            )
            
        except Exception as e:
            print(f"Error searching wishlists by email: {str(e)}")
            return WishlistSearchResponse(
                success=False,
                message=f"Error searching wishlists: {str(e)}",
                wishlists=[]
            )

    def get_shared_wishlists(self, exclude_user_id: str = None) -> List[Wishlist]:
        """Get all shared wishlists (public or anonymous) for recommendation purposes"""
        try:
            # Query wishlists where share_status is not private
            docs = self.db.collection(self.collection_name)\
                          .where("share_status", "in", [ShareType.PUBLIC.value, ShareType.ANONYMOUS.value])\
                          .stream()
            
            shared_wishlists = []
            for doc in docs:
                data = doc.to_dict()
                if data:
                    data["id"] = doc.id
                    
                    # Filter out wishlists from excluded user BEFORE expensive operations
                    if exclude_user_id:
                        wishlist_user_id = data.get('user_id', '')
                        if str(wishlist_user_id) == str(exclude_user_id):
                            print(f"🚫 FILTERING: Excluding wishlist '{data.get('name', 'Unknown')}' from user {wishlist_user_id}")
                            continue
                        else:
                            print(f"✅ INCLUDING: Wishlist '{data.get('name', 'Unknown')}' from user {wishlist_user_id}")
                    
                    # If anonymous sharing, hide user identification
                    if data.get('share_status') == ShareType.ANONYMOUS.value:
                        data['user_id'] = "anonymous"
                        data['user_email'] = "anonymous@example.com" 
                        data['user_name'] = "Anonymous User"
                    
                    # Populate product details - NOTE: This might be expensive for many wishlists
                    # Consider removing this if performance becomes an issue
                    data = self._populate_product_details(data)
                    
                    shared_wishlists.append(Wishlist(**data))
            
            print(f"📊 FILTERING RESULT: Included {len(shared_wishlists)} shared wishlists after filtering")
            return shared_wishlists
            
        except Exception as e:
            print(f"Error fetching shared wishlists: {str(e)}")
            return []

# Create global instance
wishlist_service = WishlistService()
