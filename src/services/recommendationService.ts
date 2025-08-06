import { Product } from '../contexts/ShopContext';

export interface RecommendationResponse {
  products: Product[];
  is_personalized: boolean;
  user_id: string | null;
}

const API_BASE_URL = 'http://localhost:8000';

export const recommendationService = {
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
      throw error;
    }
  },

  async getAllProducts(): Promise<Product[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/products`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching products:', error);
      throw error;
    }
  },

  async getProduct(productId: number): Promise<Product> {
    try {
      const response = await fetch(`${API_BASE_URL}/products/${productId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching product:', error);
      throw error;
    }
  }
};
