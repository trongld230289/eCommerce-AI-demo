import { Product } from '../types';

export interface RecommendationResponse {
  products: ApiProduct[];
  is_personalized: boolean;
  user_id: string | null;
}

interface ApiProduct {
  id: string;
  name: string;
  description: string;
  price: number;
  image: string;
  category: string;
  brand: string;
  inStock: boolean;
  stock: number;
  rating: number;
  reviews: number;
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

  async getAllProducts(): Promise<ApiProduct[]> {
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

  async getProduct(productId: string): Promise<ApiProduct> {
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

// Utility function to convert API product to frontend Product type
export const convertApiProductToProduct = (apiProduct: ApiProduct): Product => {
  return {
    id: apiProduct.id, // Keep as string
    name: apiProduct.name,
    description: apiProduct.description,
    price: apiProduct.price,
    image: apiProduct.image,
    category: apiProduct.category,
    brand: apiProduct.brand,
    inStock: apiProduct.inStock,
    stock: apiProduct.stock,
    rating: apiProduct.rating,
    reviews: apiProduct.reviews
  };
};
