// API service for backend integration
import { Product } from '../contexts/ShopContext';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface SearchFilters {
  category?: string;
  brand?: string;
  min_price?: number;
  max_price?: number;
  keywords?: string;
}

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  // Helper method for making API requests
  private async makeRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Product API methods
  async getAllProducts(): Promise<Product[]> {
    return this.makeRequest<Product[]>('/products');
  }

  async getProductById(id: number): Promise<Product> {
    return this.makeRequest<Product>(`/products/${id}`);
  }

  async createProduct(product: Omit<Product, 'id'>): Promise<{ success: boolean; product_id: number; data: Product }> {
    return this.makeRequest('/products', {
      method: 'POST',
      body: JSON.stringify(product),
    });
  }

  async updateProduct(id: number, product: Partial<Product>): Promise<{ success: boolean; data: Product }> {
    return this.makeRequest(`/products/${id}`, {
      method: 'PUT',
      body: JSON.stringify(product),
    });
  }

  async deleteProduct(id: number): Promise<{ success: boolean; message: string }> {
    return this.makeRequest(`/products/${id}`, {
      method: 'DELETE',
    });
  }

  // Search API methods
  async searchProducts(filters: SearchFilters): Promise<Product[]> {
    const params = new URLSearchParams();
    
    if (filters.category && filters.category !== 'All') {
      params.append('category', filters.category);
    }
    if (filters.brand && filters.brand !== 'All') {
      params.append('brand', filters.brand);
    }
    if (filters.min_price !== undefined) {
      params.append('min_price', filters.min_price.toString());
    }
    if (filters.max_price !== undefined) {
      params.append('max_price', filters.max_price.toString());
    }
    if (filters.keywords) {
      params.append('keywords', filters.keywords);
    }

    const endpoint = `/search${params.toString() ? `?${params.toString()}` : ''}`;
    return this.makeRequest<Product[]>(endpoint);
  }

  // Category and Brand API methods
  async getCategories(): Promise<{ categories: string[] }> {
    return this.makeRequest<{ categories: string[] }>('/categories');
  }

  async getBrands(): Promise<{ brands: string[] }> {
    return this.makeRequest<{ brands: string[] }>('/brands');
  }

  // Health check
  async healthCheck(): Promise<{ status: string; message: string }> {
    return this.makeRequest<{ status: string; message: string }>('/health');
  }

  // Featured Products API
  async getFeaturedProducts(limit: number = 6): Promise<Product[]> {
    return this.makeRequest<Product[]>(`/products/featured?limit=${limit}`);
  }

  // Top Products This Week API
  async getTopProductsThisWeek(limit: number = 6): Promise<Product[]> {
    return this.makeRequest<Product[]>(`/products/top-this-week?limit=${limit}`);
  }

  // Recommendations API
  async getRecommendations(userId?: string, limit: number = 4): Promise<Product[]> {
    const params = new URLSearchParams();
    if (userId) {
      params.append('user_id', userId);
    }
    params.append('limit', limit.toString());
    
    const endpoint = `/recommendations?${params.toString()}`;
    return this.makeRequest<Product[]>(endpoint);
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export individual methods for backward compatibility
export const productApi = {
  getAllProducts: () => apiService.getAllProducts(),
  getProductById: (id: number) => apiService.getProductById(id),
  searchProducts: (filters: SearchFilters) => apiService.searchProducts(filters),
  getCategories: () => apiService.getCategories(),
  getBrands: () => apiService.getBrands(),
  getFeaturedProducts: (limit?: number) => apiService.getFeaturedProducts(limit),
  getTopProductsThisWeek: (limit?: number) => apiService.getTopProductsThisWeek(limit),
  getRecommendations: (userId?: string, limit?: number) => apiService.getRecommendations(userId, limit),
};
