import { Product } from '../contexts/ShopContext';
import { apiService, SearchFilters } from './apiService';

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
      const filters: SearchFilters = {
        category: params.category,
        brand: params.brand,
        min_price: params.min_price,
        max_price: params.max_price,
        keywords: params.keywords
      };

      return await apiService.searchProducts(filters);
    } catch (error) {
      console.error('Search service error:', error);
      return [];
    }
  },

  // Additional convenience methods
  async getAllProducts(): Promise<Product[]> {
    try {
      return await apiService.getAllProducts();
    } catch (error) {
      console.error('Get all products error:', error);
      return [];
    }
  },

  async getCategories(): Promise<string[]> {
    try {
      const result = await apiService.getCategories();
      return result.categories;
    } catch (error) {
      console.error('Get categories error:', error);
      return ['All', 'Electronics'];
    }
  },

  async getBrands(): Promise<string[]> {
    try {
      const result = await apiService.getBrands();
      return result.brands;
    } catch (error) {
      console.error('Get brands error:', error);
      return ['All'];
    }
  }
};
