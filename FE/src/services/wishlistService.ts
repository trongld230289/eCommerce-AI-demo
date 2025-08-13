import { apiService } from './apiService';

export interface Product {
  id: number;
  name: string;
  price: number;
  original_price?: number;
  imageUrl: string;
  category: string;
  description?: string;
  brand?: string;
  tags?: string[];
  color?: string;
  size?: string;
  rating?: number;
  is_new?: boolean;
  discount?: number;
  created_at?: string;
  updated_at?: string;
}

export interface WishlistItem {
  product_id: number;
  added_at: number;
  product_details?: Product;
}

export interface Wishlist {
  id: string;
  user_id: string;
  name: string;
  products: WishlistItem[];
  item_count: number;
  created_at: string;
  updated_at: string;
}

export interface WishlistCreate {
  name: string;
}

export interface WishlistUpdate {
  name?: string;
}

export interface WishlistAddProduct {
  product_id: number;
}

class WishlistService {
  private baseURL = 'http://localhost:8000/api/wishlist';

  async getUserWishlists(userId: string): Promise<Wishlist[]> {
    const response = await fetch(`${this.baseURL}?user_id=${encodeURIComponent(userId)}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch wishlists');
    }
    
    return response.json();
  }

  async createWishlist(data: WishlistCreate & { user_id: string }): Promise<Wishlist> {
    const response = await fetch(this.baseURL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error('Failed to create wishlist');
    }
    
    return response.json();
  }

  async addProductToWishlist(wishlistId: string, productId: number, userId: string): Promise<Wishlist> {
    const response = await fetch(`${this.baseURL}/${wishlistId}/products?user_id=${encodeURIComponent(userId)}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ product_id: productId })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to add product to wishlist');
    }
    
    return response.json();
  }

  async removeProductFromWishlist(wishlistId: string, productId: number, userId: string): Promise<Wishlist> {
    const url = `${this.baseURL}/${wishlistId}/products/${productId}?user_id=${encodeURIComponent(userId)}`;
    console.log('[DEBUG] Removing product from wishlist:', { wishlistId, productId, userId, url });
    
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    console.log('[DEBUG] Delete response status:', response.status);
    console.log('[DEBUG] Delete response ok:', response.ok);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('[DEBUG] Delete error response:', errorText);
      throw new Error('Failed to remove product from wishlist');
    }
    
    const result = await response.json();
    console.log('[DEBUG] Delete success result:', result);
    return result;
  }

  async deleteWishlist(wishlistId: string, userId: string): Promise<void> {
    const url = `${this.baseURL}/${wishlistId}?user_id=${encodeURIComponent(userId)}`;
    console.log('[DEBUG] Deleting wishlist:', { wishlistId, userId, url });
    
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    console.log('[DEBUG] Delete wishlist response status:', response.status);
    console.log('[DEBUG] Delete wishlist response ok:', response.ok);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('[DEBUG] Delete wishlist error response:', errorText);
      throw new Error('Failed to delete wishlist');
    }
    
    const result = await response.json();
    console.log('[DEBUG] Delete wishlist success result:', result);
  }
}

export const wishlistService = new WishlistService();
