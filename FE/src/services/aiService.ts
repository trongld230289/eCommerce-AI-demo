import { Product } from '../contexts/ShopContext';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface AISearchRequest {
  query: string;
  limit?: number;
}

export interface AISearchResponse {
  status: string;
  search_intent?: {
    search_query: string;
    filters: {
      category?: string;
      min_price?: number;
      max_price?: number;
      min_rating?: number;
      min_discount?: number;
    };
  };
  products?: {
    id: number;
    name: string;
    category: string;
    price: number;
    original_price: number;
    rating: number;
    discount: number;
    imageUrl: string;
    similarity_score: number;
  }[];
  total_results?: number;
  message?: string;
}

export interface VoiceSearchResponse extends AISearchResponse {
  transcribed_text?: string;
  original_query_type?: string;
}

export const aiService = {
  async searchProducts(request: AISearchRequest): Promise<AISearchResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: AISearchResponse = await response.json();
      return data;
    } catch (error) {
      console.error('AI search error:', error);
      throw error;
    }
  },

  async embedProducts(): Promise<{ status: string; message: string; total_products?: number }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/embed-products`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Embed products error:', error);
      throw error;
    }
  },

  async getHealthStatus(): Promise<{ status: string; chromadb: string; openai: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/health`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('AI health check error:', error);
      throw error;
    }
  },

  async voiceSearch(audioFile: File, limit: number = 10): Promise<VoiceSearchResponse> {
    try {
      const formData = new FormData();
      formData.append('audio', audioFile);
      formData.append('limit', limit.toString());

      const response = await fetch(`${API_BASE_URL}/api/ai/search-by-voice`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: VoiceSearchResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Voice search error:', error);
      throw error;
    }
  },

  async transcribeAudio(audioFile: File): Promise<{ status: string; text?: string; message?: string }> {
    try {
      const formData = new FormData();
      formData.append('audio', audioFile);

      const response = await fetch(`${API_BASE_URL}/api/ai/transcribe`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Audio transcription error:', error);
      throw error;
    }
  },

  // Convert AI search results to Product format for compatibility
  convertToProducts(aiProducts: AISearchResponse['products']): Product[] {
    if (!aiProducts) return [];
    
    return aiProducts.map(aiProduct => ({
      id: aiProduct.id,
      name: aiProduct.name,
      price: aiProduct.price,
      original_price: aiProduct.original_price,
      imageUrl: aiProduct.imageUrl,
      category: aiProduct.category,
      description: '', // Not provided by AI search
      rating: aiProduct.rating,
      discount: aiProduct.discount,
      created_at: undefined,
      updated_at: undefined
    }));
  }
};
