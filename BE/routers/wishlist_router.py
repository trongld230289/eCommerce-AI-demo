from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from models import Wishlist, WishlistCreate, WishlistUpdate, WishlistAddProduct, WishlistRemoveProduct
from services.wishlist_service import wishlist_service
from auth import get_current_user

router = APIRouter(prefix="/api/wishlist", tags=["wishlist"])

@router.get("/", response_model=List[Wishlist])
def get_user_wishlists(current_user: dict = Depends(get_current_user)):
    """Get all wishlists for the current user"""
    try:
        user_id = current_user.get("uid")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        wishlists = wishlist_service.get_user_wishlists(user_id)
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
        
        # Override user_id from token
        wishlist_data.user_id = user_id
        
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
        raise HTTPException(status_code=500, detail=str(e))

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
