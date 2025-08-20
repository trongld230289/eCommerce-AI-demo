<<<<<<< HEAD
import { apiService } from './apiService';
=======
import { getAuth } from 'firebase/auth';
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e

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

<<<<<<< HEAD
export interface Wishlist {
  id: string;
  user_id: string;
  name: string;
  products: WishlistItem[];
  item_count: number;
=======
export enum ShareType {
  PRIVATE = 'private',
  PUBLIC = 'public',
  ANONYMOUS = 'anonymous'
}

export interface Wishlist {
  id: string;
  user_id: string;
  user_email?: string;
  user_name?: string;
  name: string;
  products: WishlistItem[];
  item_count: number;
  share_status: ShareType;
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
  created_at: string;
  updated_at: string;
}

export interface WishlistCreate {
  name: string;
}

export interface WishlistUpdate {
  name?: string;
<<<<<<< HEAD
=======
  share_status?: ShareType;
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
}

export interface WishlistAddProduct {
  product_id: number;
}

<<<<<<< HEAD
class WishlistService {
  private baseURL = 'http://localhost:8000/api/wishlist';

  async getUserWishlists(userId: string): Promise<Wishlist[]> {
    const response = await fetch(`${this.baseURL}?user_id=${encodeURIComponent(userId)}`, {
      method: 'GET',
      headers: {
=======
export interface WishlistShareUpdate {
  share_status: ShareType;
}

export interface WishlistShareResponse {
  success: boolean;
  message: string;
  share_status: ShareType;
  share_url?: string;
}

export interface WishlistSearchRequest {
  email: string;
}

export interface WishlistSearchResult {
  id: string;
  name: string;
  user_email?: string;
  user_name?: string;
  share_status: ShareType;
  item_count: number;
  created_at: number;
}

export interface WishlistSearchResponse {
  success: boolean;
  message: string;
  wishlists: WishlistSearchResult[];
}

class WishlistService {
  private baseURL = `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/wishlist`;

  private async getAuthHeaders(): Promise<{ [key: string]: string }> {
    try {
      const auth = getAuth();
      const user = auth.currentUser;
      
      if (user) {
        const token = await user.getIdToken();
        return {
          'Authorization': `Bearer ${token}`
        };
      }
      
      return {};
    } catch (error) {
      console.error('Error getting auth token:', error);
      return {};
    }
  }

  async getUserWishlists(userId: string): Promise<Wishlist[]> {
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(`${this.baseURL}?user_id=${encodeURIComponent(userId)}`, {
      method: 'GET',
      headers: {
        ...headers,
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
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
<<<<<<< HEAD
    const response = await fetch(`${this.baseURL}/${wishlistId}/products?user_id=${encodeURIComponent(userId)}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
=======
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${this.baseURL}/${wishlistId}/products?user_id=${encodeURIComponent(userId)}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...headers
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
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
    
<<<<<<< HEAD
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
=======
    const headers = await this.getAuthHeaders();
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...headers
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
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
    
<<<<<<< HEAD
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
=======
    const headers = await this.getAuthHeaders();
    
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        ...headers,
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
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
<<<<<<< HEAD
=======

  async updateShareStatus(wishlistId: string, userId: string, shareUpdate: WishlistShareUpdate): Promise<WishlistShareResponse> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`${this.baseURL}/${wishlistId}/share?user_id=${encodeURIComponent(userId)}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      body: JSON.stringify(shareUpdate)
    });
    
    if (!response.ok) {
      throw new Error('Failed to update share status');
    }
    
    return response.json();
  }

  async getSharedWishlist(wishlistId: string): Promise<Wishlist> {
    const response = await fetch(`${this.baseURL}/shared/${wishlistId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch shared wishlist');
    }
    
    return response.json();
  }

  async searchWishlists(email: string): Promise<WishlistSearchResponse> {
    const response = await fetch(`${this.baseURL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email: email.toLowerCase() })
    });
    
    if (!response.ok) {
      throw new Error('Failed to search wishlists');
    }
    
    return response.json();
  }

  async addFromSharedWishlist(
    sharedWishlistId: string, 
    productId: number, 
    targetWishlistId: string,
    userId: string
  ): Promise<void> {
    const response = await fetch(
      `${this.baseURL}/shared/${sharedWishlistId}/add-to-my-wishlist/${productId}?target_wishlist_id=${encodeURIComponent(targetWishlistId)}&user_id=${encodeURIComponent(userId)}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(await this.getAuthHeaders())
        }
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to add product from shared wishlist');
    }
    
    return response.json();
  }
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
}

export const wishlistService = new WishlistService();
