import { Product } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export interface SearchParams {
  category?: string;
  brand?: string;
  min_price?: number;
  max_price?: number;
  keywords?: string;
}

export const searchService = {
  async searchProducts(params: SearchParams): Promise<Product[]> {
    try {
      const searchParams = new URLSearchParams();
      
      if (params.category) searchParams.append('category', params.category);
      if (params.brand) searchParams.append('brand', params.brand);
      if (params.min_price !== undefined) searchParams.append('min_price', params.min_price.toString());
      if (params.max_price !== undefined) searchParams.append('max_price', params.max_price.toString());
      if (params.keywords) searchParams.append('keywords', params.keywords);

      const response = await fetch(`${API_BASE_URL}/search?${searchParams}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const products = await response.json();
      return products;
    } catch (error) {
      console.error('Search service error:', error);
      return [];
    }
  }
};
