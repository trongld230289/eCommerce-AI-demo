const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface ProductSuggestion {
  id: number;
  name: string;
  price: number;
  original_price?: number;
  category: string;
  imageUrl: string;
  description?: string;
  rating?: number;
  discount?: number;
}

export interface WishlistRecommendation {
  query: string;
  product_query_id: number;
  suggestion: string;
  product_suggestion: ProductSuggestion;
}

export interface SingleProductRecommendationRequest {
  user_id: string;
  product_id: number;
}

export interface SingleProductRecommendationResponse {
  status: string;
  recommendation?: WishlistRecommendation;
  message?: string;
}

class WishlistRecommendationsService {
  private baseURL = `${API_BASE_URL}/api/wishlist`;

  private async getAuthHeaders(): Promise<{ [key: string]: string }> {
    const token = localStorage.getItem('token');
    const headers: { [key: string]: string } = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
  }

  async getSingleProductRecommendation(productId: number, userId?: string): Promise<WishlistRecommendation | null> {
    try {
      const headers = await this.getAuthHeaders();
      
      // Get user ID from localStorage if not provided
      const currentUserId = userId || localStorage.getItem('userId') || localStorage.getItem('user_id');
      
      if (!currentUserId) {
        console.warn('No user ID available for single product recommendation');
        return null;
      }

      const requestBody: SingleProductRecommendationRequest = {
        user_id: currentUserId,
        product_id: productId
      };
      
      console.log('🚀 Sending single product recommendation request:', requestBody);
      
      const response = await fetch(`${this.baseURL}/recommendation/single`, {
        method: 'POST',
        headers,
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const result: SingleProductRecommendationResponse = await response.json();
      return result.recommendation || null;
    } catch (error) {
      console.error('Error getting single product recommendation:', productId, error);
      return null;
    }
  }

  async getSingleProductRecommendations(productIds: number[], userId?: string): Promise<Map<number, WishlistRecommendation>> {
    try {
      const currentUserId = userId || localStorage.getItem('userId') || localStorage.getItem('user_id');
      
      if (!currentUserId) {
        console.warn('No user ID available for recommendations');
        return new Map();
      }

      console.log('🚀 Fetching individual recommendations for products:', productIds, 'User:', currentUserId);
      
      // Call API for each product individually in parallel
      const promises = productIds.map(productId => 
        this.getSingleProductRecommendation(productId, currentUserId)
      );
      
      const recommendations = await Promise.all(promises);
      const recommendationMap = new Map<number, WishlistRecommendation>();
      
      recommendations.forEach((rec, index) => {
        if (rec) {
          recommendationMap.set(productIds[index], rec);
        }
      });
      
      console.log('✅ Individual recommendations loaded:', recommendationMap.size);
      return recommendationMap;
    } catch (error) {
      console.error('Error getting single product recommendations:', productIds, error);
      return new Map();
    }
  }

  // Convenience method for loading recommendations on page load
  async loadRecommendationsOnPageLoad(productIds: number[], userId?: string): Promise<Map<number, WishlistRecommendation>> {
    if (!productIds || productIds.length === 0) {
      console.log('📝 No products to load recommendations for');
      return new Map();
    }

    console.log('📄 Page Load: Loading recommendations for', productIds.length, 'products');
    return this.getSingleProductRecommendations(productIds, userId);
  }

  // Method to load recommendations with individual loading states
  async loadRecommendationsWithProgress(
    productIds: number[], 
    userId?: string,
    onProductLoadingChange?: (productId: number, loading: boolean) => void,
    onRecommendationLoaded?: (productId: number, recommendation: WishlistRecommendation | null) => void
  ): Promise<Map<number, WishlistRecommendation>> {
    try {
      const currentUserId = userId || localStorage.getItem('userId') || localStorage.getItem('user_id');
      
      if (!currentUserId) {
        console.warn('No user ID available for recommendations');
        return new Map();
      }

      console.log('🚀 Loading recommendations with progress for products:', productIds, 'User:', currentUserId);
      
      // Set all products as loading
      productIds.forEach(productId => {
        onProductLoadingChange?.(productId, true);
      });

      const recommendationMap = new Map<number, WishlistRecommendation>();
      
      // Process each product individually to show progressive loading
      const promises = productIds.map(async (productId) => {
        try {
          const recommendation = await this.getSingleProductRecommendation(productId, currentUserId);
          
          // Notify about loaded recommendation
          onRecommendationLoaded?.(productId, recommendation);
          
          if (recommendation) {
            recommendationMap.set(productId, recommendation);
          }
          
          return { productId, recommendation };
        } catch (error) {
          console.error(`Error loading recommendation for product ${productId}:`, error);
          return { productId, recommendation: null };
        } finally {
          // Set loading to false for this product
          onProductLoadingChange?.(productId, false);
        }
      });
      
      await Promise.all(promises);
      
      console.log('✅ Progressive loading completed:', recommendationMap.size, 'recommendations loaded');
      return recommendationMap;
    } catch (error) {
      console.error('Error loading recommendations with progress:', productIds, error);
      // Clear all loading states on error
      productIds.forEach(productId => {
        onProductLoadingChange?.(productId, false);
      });
      return new Map();
    }
  }
}

export const wishlistRecommendationsService = new WishlistRecommendationsService();
