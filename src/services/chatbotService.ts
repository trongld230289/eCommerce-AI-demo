import { Product } from '../contexts/ShopContext';

const API_BASE_URL = 'http://localhost:8000';

export interface ChatbotRequest {
  message: string;
  user_id?: string;
}

export interface ChatbotResponse {
  response: string;
  products: Product[];
  search_params: Record<string, any>;
  should_redirect?: boolean;
  redirect_url?: string;
}

export const chatbotService = {
  async sendMessage(request: ChatbotRequest): Promise<ChatbotResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/chatbot`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Debug logging
      console.log('Chatbot API response:', data);
      console.log('Products returned:', data.products);
      
      // Check if this is a product search query
      const hasSearchParams = data.search_params && (
        data.search_params.category || 
        data.search_params.brand || 
        data.search_params.min_price || 
        data.search_params.max_price ||
        data.search_params.keywords
      );

      if (hasSearchParams && data.products && data.products.length > 0) {
        // Create search URL
        const searchParams = new URLSearchParams();
        
        if (data.search_params.category) {
          searchParams.append('category', data.search_params.category);
        }
        if (data.search_params.brand) {
          searchParams.append('brand', data.search_params.brand);
        }
        if (data.search_params.min_price) {
          searchParams.append('minPrice', data.search_params.min_price.toString());
        }
        if (data.search_params.max_price) {
          searchParams.append('maxPrice', data.search_params.max_price.toString());
        }
        if (data.search_params.keywords) {
          const keywordsString = Array.isArray(data.search_params.keywords) 
            ? data.search_params.keywords.join(' ') 
            : data.search_params.keywords;
          searchParams.append('q', keywordsString);
          // Also add chatbot parameter to indicate this is from chatbot
          searchParams.append('chatbot', keywordsString);
        }

        return {
          ...data,
          should_redirect: true,
          redirect_url: `/products?${searchParams.toString()}`
        };
      }

      return data;
    } catch (error) {
      console.error('Chatbot service error:', error);
      // Fallback response
      return {
        response: "I'm sorry, I'm having trouble processing your request right now. Please try again later.",
        products: [],
        search_params: {}
      };
    }
  }
};
