import { Product } from '../contexts/ShopContext';
import { apiService } from './apiService';

export interface RecommendationResponse {
  products: Product[];
  is_personalized: boolean;
  user_id: string | null;
}

const LEGACY_API_BASE_URL = 'http://localhost:8000';

export const recommendationService = {
  async getRecommendations(userId?: string, limit: number = 10): Promise<RecommendationResponse> {
    try {
      // Try to use the AI_Service recommendations endpoint first
      const params = new URLSearchParams();
      if (userId) {
        params.append('user_id', userId);
      }
      params.append('limit', limit.toString());

      const response = await fetch(`${LEGACY_API_BASE_URL}/recommendations?${params}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Check if data is an array (direct product list) or object with products
      if (Array.isArray(data)) {
        return {
          products: data,
          is_personalized: Boolean(userId),
          user_id: userId || null
        };
      } else if (data && data.products) {
        return data;
      } else {
        throw new Error('Invalid response format');
      }
    } catch (error) {
      console.error('Error fetching recommendations, falling back to all products:', error);
      
      // Fallback: return some products from the new API
      try {
        const products = await apiService.getAllProducts();
        return {
          products: products.slice(0, limit),
          is_personalized: false,
          user_id: userId || null
        };
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError);
        throw error;
      }
    }
  },

  async getAllProducts(): Promise<Product[]> {
    try {
      return await apiService.getAllProducts();
    } catch (error) {
      console.error('Error fetching products:', error);
      throw error;
    }
  },

  async getProduct(productId: number): Promise<Product> {
    try {
      return await apiService.getProductById(productId);
    } catch (error) {
      console.error('Error fetching product:', error);
      throw error;
    }
  }
};
