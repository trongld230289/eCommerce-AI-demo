import { Product } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export interface RecommendationResponse {
  products: Product[];
  is_personalized: boolean;
  user_id: string | null;
}

class RecommendationService {
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
      return data;
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      // Return fallback empty response
      return {
        products: [],
        is_personalized: false,
        user_id: null
      };
    }
  }

  async getAllProducts(): Promise<Product[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/products`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const products = await response.json();
      return products;
    } catch (error) {
      console.error('Error fetching products:', error);
      return [];
    }
  }

  async getProduct(productId: string): Promise<Product | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/products/${productId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const product = await response.json();
      return product;
    } catch (error) {
      console.error('Error fetching product:', error);
      return null;
    }
  }

  async getRecommendationsByCategory(category: string, limit: number = 5): Promise<Product[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/recommendations/category/${category}?limit=${limit}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data.products || [];
    } catch (error) {
      console.error('Error fetching category recommendations:', error);
      return [];
    }
  }
}

export const recommendationService = new RecommendationService();
