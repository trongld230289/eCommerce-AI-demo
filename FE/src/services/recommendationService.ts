import { Product } from '../contexts/ShopContext';

export interface RecommendationResponse {
  recommendations?: Product[];
  products?: Product[];
  user_id: string | null;
  source?: string;
  count?: number;
  timestamp?: string;
}

export interface UserEvent {
  user_id: string;
  event_type: 'view' | 'add_to_cart' | 'remove_from_cart' | 'add_to_wishlist' | 'remove_from_wishlist' | 'purchase';
  product_id: string | number;
  session_id?: string;
  metadata?: Record<string, any>;
}

export interface SmartSearchRequest {
  query: string;
  limit?: number;
}

export interface SmartSearchResponse {
  query: string;
  results: Product[];
  parsed_filters: Record<string, any>;
  total_found: number;
  search_type: string;
  timestamp: string;
}

const API_BASE_URL = 'http://localhost:8000';

export const recommendationService = {
  // Get personalized recommendations from the new integrated system
  async getRecommendations(userId?: string, limit: number = 10): Promise<RecommendationResponse> {
    try {
      const params = new URLSearchParams();
      if (userId) {
        params.append('user_id', userId);
      }
      params.append('limit', limit.toString());

      const response = await fetch(`${API_BASE_URL}/recommendations?${params}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Handle different response formats
      if (data.recommendations) {
        // New format with recommendations array
        return {
          recommendations: data.recommendations,
          products: data.recommendations, // For compatibility
          user_id: data.user_id || userId || null,
          source: data.source || 'backend_api',
          count: data.count,
          timestamp: data.timestamp
        };
      } else if (Array.isArray(data)) {
        // Legacy format - direct product array
        return {
          products: data,
          recommendations: data,
          user_id: userId || null,
          source: 'legacy_api'
        };
      } else {
        throw new Error('Invalid response format');
      }
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      throw error;
    }
  },

  // Track user events for better recommendations
  async trackUserEvent(eventData: UserEvent): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/track-event`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(eventData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return result.success || false;
    } catch (error) {
      console.error('Error tracking user event:', error);
      return false;
    }
  },

  // Smart search with natural language processing
  async smartSearch(searchRequest: SmartSearchRequest): Promise<SmartSearchResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/search/smart`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchRequest)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error performing smart search:', error);
      throw error;
    }
  },

  // Check recommendation system health
  async checkSystemHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/recommendation-health`);
      if (!response.ok) {
        return false;
      }
      
      const data = await response.json();
      return data.recommendation_system_available || false;
    } catch (error) {
      console.error('Error checking recommendation system health:', error);
      return false;
    }
  },

  // Get all products (fallback)
  async getAllProducts(): Promise<Product[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/products`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching products:', error);
      throw error;
    }
  },

  // Get single product
  async getProduct(productId: number): Promise<Product> {
    try {
      const response = await fetch(`${API_BASE_URL}/products/${productId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching product:', error);
      throw error;
    }
  }
};
