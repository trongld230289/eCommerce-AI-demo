from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List
from models import (
    Wishlist, WishlistCreate, WishlistUpdate, WishlistAddProduct, 
    WishlistRemoveProduct, WishlistShareUpdate, WishlistShareResponse,
    WishlistSearchRequest, WishlistSearchResponse
)
from services.wishlist_service import wishlist_service
from auth import get_current_user

router = APIRouter(prefix="/api/wishlist", tags=["wishlist"])

@router.get("/debug-auth")
def debug_auth(current_user: dict = Depends(get_current_user)):
    """Debug endpoint to check authentication"""
    print(f"DEBUG AUTH ENDPOINT: current_user = {current_user}")
    return {
        "message": "Authentication debug",
        "user_data": current_user
    }

@router.get("/", response_model=List[Wishlist])
def get_user_wishlists(current_user: dict = Depends(get_current_user)):
    """Get all wishlists for the current user"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        user_email = current_user.get("email")
        user_name = current_user.get("name")
        
        wishlists = wishlist_service.get_user_wishlists(user_id, user_email, user_name)
        return wishlists
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Wishlist)
def create_wishlist(
    wishlist_data: WishlistCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new wishlist"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        # Debug logging
        print(f"Router: Creating wishlist for user:")
        print(f"  current_user: {current_user}")
        print(f"  current_user type: {type(current_user)}")
        print(f"  current_user keys: {list(current_user.keys()) if isinstance(current_user, dict) else 'Not a dict'}")
        
        # Extract user info
        user_email = current_user.get("email")
        user_name = current_user.get("name")
        
        print(f"Router: Extracted user info:")
        print(f"  user_email: {user_email} (type: {type(user_email)})")
        print(f"  user_name: {user_name} (type: {type(user_name)})")
        
        # Override user data from token
        wishlist_data.user_id = user_id
        wishlist_data.user_email = user_email
        wishlist_data.user_name = user_name
        
        print(f"Router: Updated wishlist_data:")
        print(f"  user_id: {wishlist_data.user_id}")
        print(f"  user_email: {wishlist_data.user_email}")
        print(f"  user_name: {wishlist_data.user_name}")
        
        wishlist = wishlist_service.create_wishlist(wishlist_data)
        return wishlist
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{wishlist_id}", response_model=Wishlist)
def get_wishlist(
    wishlist_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific wishlist"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        wishlist = wishlist_service.get_wishlist(wishlist_id, user_id)
        if not wishlist:
            raise HTTPException(status_code=404, detail="Wishlist not found")
        
        return wishlist
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{wishlist_id}", response_model=Wishlist)
def update_wishlist(
    wishlist_id: str,
    update_data: WishlistUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update wishlist name"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        wishlist = wishlist_service.update_wishlist(wishlist_id, user_id, update_data)
        if not wishlist:
            raise HTTPException(status_code=404, detail="Wishlist not found")
        
        return wishlist
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{wishlist_id}")
def delete_wishlist(
    wishlist_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a wishlist"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        success = wishlist_service.delete_wishlist(wishlist_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Wishlist not found")
        
        return {"message": "Wishlist deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "permission" in error_msg.lower():
            raise HTTPException(status_code=403, detail=error_msg)
        else:
            raise HTTPException(status_code=500, detail=error_msg)

@router.post("/{wishlist_id}/products", response_model=Wishlist)
def add_product_to_wishlist(
    wishlist_id: str,
    product_data: WishlistAddProduct,
    current_user: dict = Depends(get_current_user)
):
    """Add a product to wishlist"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        wishlist = wishlist_service.add_product_to_wishlist(
            wishlist_id, user_id, product_data.product_id
        )
        # Thuong implementation - add product to wishlist
        if not wishlist:
            raise HTTPException(status_code=404, detail="Wishlist not found")
        
        return wishlist
    except HTTPException:
        raise
    except Exception as e:
        if "already in wishlist" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        if "Product not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{wishlist_id}/products/{product_id}", response_model=Wishlist)
def remove_product_from_wishlist(
    wishlist_id: str,
    product_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Remove a product from wishlist"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        wishlist = wishlist_service.remove_product_from_wishlist(
            wishlist_id, user_id, product_id
        )
        # Thuong implementation - remove product from wishlist
        if not wishlist:
            raise HTTPException(status_code=404, detail="Wishlist not found")
        
        return wishlist
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{wishlist_id}/clear", response_model=Wishlist)
def clear_wishlist(
    wishlist_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Clear all products from wishlist"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        wishlist = wishlist_service.clear_wishlist(wishlist_id, user_id)
        if not wishlist:
            raise HTTPException(status_code=404, detail="Wishlist not found")
        
        return wishlist
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{wishlist_id}/share", response_model=WishlistShareResponse)
def update_wishlist_share_status(
    wishlist_id: str,
    share_update: WishlistShareUpdate,
    user_id: str = Query(...)
):
    """Update wishlist share status"""
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        result = wishlist_service.update_share_status(wishlist_id, user_id, share_update)
        # Thuong implementation - share and unshared wishlist
        if not result.success:
            if "not found" in result.message.lower():
                raise HTTPException(status_code=404, detail=result.message)
            elif "unauthorized" in result.message.lower():
                raise HTTPException(status_code=403, detail=result.message)
            else:
                raise HTTPException(status_code=500, detail=result.message)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/shared/{wishlist_id}", response_model=Wishlist)
def get_shared_wishlist(wishlist_id: str):
    """Get a shared wishlist (public access, no authentication required)"""
    try:
        wishlist = wishlist_service.get_shared_wishlist(wishlist_id)
        if not wishlist:
            raise HTTPException(
                status_code=404, 
                detail="Shared wishlist not found or is private"
            )
        
        return wishlist
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=WishlistSearchResponse)
def search_wishlists(search_request: WishlistSearchRequest):
    """Search for shared wishlists by email (public access, no authentication required)"""
    try:
        if not search_request.email or not search_request.email.strip():
            raise HTTPException(status_code=400, detail="Email is required")
        
        result = wishlist_service.search_wishlists_by_email(search_request.email.strip().lower())
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/shared/{wishlist_id}/add-to-my-wishlist/{product_id}")
def add_from_shared_wishlist(
    wishlist_id: str,
    product_id: int,
    target_wishlist_id: str = Query(..., description="User's wishlist ID to add the product to"),
    current_user: dict = Depends(get_current_user)
):
    """Add a product from a shared wishlist to user's own wishlist"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        result = wishlist_service.add_product_to_shared_wishlist(
            wishlist_id, product_id, target_wishlist_id, user_id
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Wishlist not found or unauthorized")
        
        return {"message": "Product added to your wishlist successfully"}
    except HTTPException:
        raise
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))
