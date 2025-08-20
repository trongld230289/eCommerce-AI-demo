from typing import List, Optional, Dict, Any
from datetime import datetime
import time
from firebase_config import get_firestore_db
from models import Cart, CartItem, CartCreate, CartAddItem, CartUpdateItem, CartRemoveItem, Product
from product_service import product_service

class CartService:
    def __init__(self):
        self.db = get_firestore_db()
        self.collection_name = "carts"
    
    def _get_collection(self):
        """Get the carts collection reference"""
        if not self.db:
            raise Exception("Firestore database not initialized")
        return self.db.collection(self.collection_name)
    
    def _cart_doc_to_dict(self, doc) -> Dict[str, Any]:
        """Convert Firestore document to dictionary"""
        cart_data = doc.to_dict()
        cart_data['id'] = doc.id
        return cart_data
    
    def _calculate_cart_totals(self, items: List[CartItem]) -> Dict[str, Any]:
        """Calculate cart totals and item count"""
        item_count = sum(item.quantity for item in items)
<<<<<<< HEAD
        total_amount = sum(item.quantity * item.product_details.price for item in items if item.product_details)
=======
        total_amount = sum(item.quantity * item.product_details['price'] for item in items if item.product_details)
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
        return {
            "item_count": item_count,
            "total_amount": round(total_amount, 2)
        }
    
    async def get_or_create_cart(self, user_id: str) -> Cart:
        """Get user's cart or create a new one if it doesn't exist"""
        try:
            collection = self._get_collection()
            
            # Query for existing cart
            query = collection.where("user_id", "==", user_id).limit(1)
            docs = query.get()
            
            if docs:
                # Cart exists, return it
                doc = docs[0]
                cart_data = self._cart_doc_to_dict(doc)
                
                # Load product details for each item
                items_with_details = []
                for item_data in cart_data.get('items', []):
                    product = product_service.get_product_by_id(item_data['product_id'])
                    cart_item = CartItem(
                        product_id=item_data['product_id'],
                        quantity=item_data['quantity'],
                        added_at=item_data['added_at'],
                        product_details=product
                    )
                    items_with_details.append(cart_item)
                
                # Calculate totals
                totals = self._calculate_cart_totals(items_with_details)
                
                cart = Cart(
                    id=cart_data['id'],
                    user_id=cart_data['user_id'],
                    items=items_with_details,
                    item_count=totals['item_count'],
                    total_amount=totals['total_amount'],
                    created_at=cart_data['created_at'],
                    updated_at=cart_data['updated_at']
                )
                return cart
            else:
                # Create new cart
                current_time = time.time()
                cart_data = {
                    "user_id": user_id,
                    "items": [],
                    "item_count": 0,
                    "total_amount": 0.0,
                    "created_at": current_time,
                    "updated_at": current_time
                }
                
                doc_ref = collection.add(cart_data)
                cart_id = doc_ref[1].id
                
                print(f"✅ Created new cart with ID: {cart_id} for user: {user_id}")
                
                cart = Cart(
                    id=cart_id,
                    user_id=user_id,
                    items=[],
                    item_count=0,
                    total_amount=0.0,
                    created_at=current_time,
                    updated_at=current_time
                )
                return cart
                
        except Exception as e:
            print(f"Error getting/creating cart: {e}")
            raise Exception(f"Failed to get or create cart: {str(e)}")
    
    async def add_item_to_cart(self, user_id: str, cart_add_item: CartAddItem) -> Cart:
        """Add item to cart or update quantity if item already exists"""
        try:
            print(f"🛒 Adding item to cart - User: {user_id}, Product: {cart_add_item.product_id}, Quantity: {cart_add_item.quantity}")
            
            cart = await self.get_or_create_cart(user_id)
            print(f"📦 Current cart has {len(cart.items)} items")
            
            collection = self._get_collection()
            
            # Check if product exists
            product = product_service.get_product_by_id(cart_add_item.product_id)
            if not product:
                raise Exception(f"Product with ID {cart_add_item.product_id} not found")
            
            print(f"✅ Product found: {product.get('name', 'Unknown')}")
            
            # Find existing item in cart
            existing_item_index = None
            for i, item in enumerate(cart.items):
                if item.product_id == cart_add_item.product_id:
                    existing_item_index = i
                    break
            
            current_time = time.time()
            
            if existing_item_index is not None:
                # Update existing item quantity
                print(f"📝 Updating existing item at index {existing_item_index}")
                cart.items[existing_item_index].quantity += cart_add_item.quantity
                cart.items[existing_item_index].product_details = product
            else:
                # Add new item
                print(f"➕ Adding new item to cart")
                new_item = CartItem(
                    product_id=cart_add_item.product_id,
                    quantity=cart_add_item.quantity,
                    added_at=current_time,
                    product_details=product
                )
                cart.items.append(new_item)
                print(f"📦 Cart now has {len(cart.items)} items")
            
            # Convert items to dict format for Firestore
            items_data = []
            for item in cart.items:
                items_data.append({
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "added_at": item.added_at
                })
            
            print(f"💾 Saving {len(items_data)} items to Firestore")
            
            # Calculate new totals
            totals = self._calculate_cart_totals(cart.items)
            
            # Update cart in Firestore
            cart_ref = collection.document(cart.id)
            update_data = {
                "items": items_data,
                "item_count": totals['item_count'],
                "total_amount": totals['total_amount'],
                "updated_at": current_time
            }
            
            print(f"🔄 Updating Firebase with: {update_data}")
            cart_ref.update(update_data)
            
            # Update cart object
            cart.item_count = totals['item_count']
            cart.total_amount = totals['total_amount']
            cart.updated_at = current_time
            
            return cart
            
        except Exception as e:
            print(f"Error adding item to cart: {e}")
            raise Exception(f"Failed to add item to cart: {str(e)}")
    
    async def update_item_quantity(self, user_id: str, cart_update_item: CartUpdateItem) -> Cart:
        """Update item quantity in cart"""
        try:
            cart = await self.get_or_create_cart(user_id)
            collection = self._get_collection()
            
            # Find item in cart
            item_found = False
            for item in cart.items:
                if item.product_id == cart_update_item.product_id:
                    if cart_update_item.quantity <= 0:
                        # Remove item if quantity is 0 or negative
                        cart.items.remove(item)
                    else:
                        # Update quantity
                        item.quantity = cart_update_item.quantity
                    item_found = True
                    break
            
            if not item_found:
                raise Exception(f"Product with ID {cart_update_item.product_id} not found in cart")
            
            # Convert items to dict format for Firestore
            items_data = []
            for item in cart.items:
                items_data.append({
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "added_at": item.added_at
                })
            
            # Calculate new totals
            totals = self._calculate_cart_totals(cart.items)
            current_time = time.time()
            
            # Update cart in Firestore
            cart_ref = collection.document(cart.id)
            cart_ref.update({
                "items": items_data,
                "item_count": totals['item_count'],
                "total_amount": totals['total_amount'],
                "updated_at": current_time
            })
            
            # Update cart object
            cart.item_count = totals['item_count']
            cart.total_amount = totals['total_amount']
            cart.updated_at = current_time
            
            return cart
            
        except Exception as e:
            print(f"Error updating item quantity: {e}")
            raise Exception(f"Failed to update item quantity: {str(e)}")
    
    async def remove_item_from_cart(self, user_id: str, cart_remove_item: CartRemoveItem) -> Cart:
        """Remove item from cart"""
        try:
            cart = await self.get_or_create_cart(user_id)
            collection = self._get_collection()
            
            # Find and remove item from cart
            item_found = False
            for item in cart.items:
                if item.product_id == cart_remove_item.product_id:
                    cart.items.remove(item)
                    item_found = True
                    break
            
            if not item_found:
                raise Exception(f"Product with ID {cart_remove_item.product_id} not found in cart")
            
            # Convert items to dict format for Firestore
            items_data = []
            for item in cart.items:
                items_data.append({
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "added_at": item.added_at
                })
            
            # Calculate new totals
            totals = self._calculate_cart_totals(cart.items)
            current_time = time.time()
            
            # Update cart in Firestore
            cart_ref = collection.document(cart.id)
            cart_ref.update({
                "items": items_data,
                "item_count": totals['item_count'],
                "total_amount": totals['total_amount'],
                "updated_at": current_time
            })
            
            # Update cart object
            cart.item_count = totals['item_count']
            cart.total_amount = totals['total_amount']
            cart.updated_at = current_time
            
            return cart
            
        except Exception as e:
            print(f"Error removing item from cart: {e}")
            raise Exception(f"Failed to remove item from cart: {str(e)}")
    
    async def clear_cart(self, user_id: str) -> Cart:
        """Clear all items from cart"""
        try:
            cart = await self.get_or_create_cart(user_id)
            collection = self._get_collection()
            
            current_time = time.time()
            
            # Update cart in Firestore
            cart_ref = collection.document(cart.id)
            cart_ref.update({
                "items": [],
                "item_count": 0,
                "total_amount": 0.0,
                "updated_at": current_time
            })
            
            # Update cart object
            cart.items = []
            cart.item_count = 0
            cart.total_amount = 0.0
            cart.updated_at = current_time
            
            return cart
            
        except Exception as e:
            print(f"Error clearing cart: {e}")
            raise Exception(f"Failed to clear cart: {str(e)}")
    
    async def get_cart(self, user_id: str) -> Cart:
        """Get user's cart"""
        return await self.get_or_create_cart(user_id)
    
    async def sync_cart_from_frontend(self, user_id: str, frontend_cart: List[Dict[str, Any]]) -> Cart:
        """Sync cart from frontend localStorage to Firebase"""
        try:
            cart = await self.get_or_create_cart(user_id)
            collection = self._get_collection()
            
            # Clear existing items
            cart.items = []
            
            # Add all items from frontend
            for frontend_item in frontend_cart:
                product_id = frontend_item.get('id')
                quantity = frontend_item.get('quantity', 1)
                
                # Get product details
                product = product_service.get_product_by_id(product_id)
                if product:
                    cart_item = CartItem(
                        product_id=product_id,
                        quantity=quantity,
                        added_at=time.time(),
                        product_details=product
                    )
                    cart.items.append(cart_item)
            
            # Convert items to dict format for Firestore
            items_data = []
            for item in cart.items:
                items_data.append({
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "added_at": item.added_at
                })
            
            # Calculate new totals
            totals = self._calculate_cart_totals(cart.items)
            current_time = time.time()
            
            # Update cart in Firestore
            cart_ref = collection.document(cart.id)
            cart_ref.update({
                "items": items_data,
                "item_count": totals['item_count'],
                "total_amount": totals['total_amount'],
                "updated_at": current_time
            })
            
            # Update cart object
            cart.item_count = totals['item_count']
            cart.total_amount = totals['total_amount']
            cart.updated_at = current_time
            
            return cart
            
        except Exception as e:
            print(f"Error syncing cart: {e}")
            raise Exception(f"Failed to sync cart: {str(e)}")

# Global cart service instance
cart_service = CartService()
