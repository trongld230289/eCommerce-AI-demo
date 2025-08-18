import { Product } from '../contexts/ShopContext';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface ConversationMessage {
  role: string; // "user" or "assistant"
  content: string;
}

export interface ChatbotRequest {
  message: string;
  user_id?: string;
  conversation_history?: ConversationMessage[];
}

export interface ChatbotResponse {
  response: string;
  products: Product[];
  search_params: Record<string, any>;
  redirect_url?: string;
  page_code?: string;
  smart_search_used?: boolean;
  parsed_filters?: Record<string, any>;
  function_used?: string;
  language_detected?: string;
  conversation_context?: {
    current_function: string;
    messages: Array<{
      user_input: string;
      function_used: string;
      language: string;
      agent_output: string;
    }>;
  };
  // Add messages field to match backend
  messages?: Array<{
    user_input: string;
    function_used: string;
    language: string;
    agent_output: string;
  }>;
}

export const chatbotService = {
  async sendMessage(request: ChatbotRequest): Promise<ChatbotResponse> {
    try {
      // Call the new AI search middleware endpoint
      const response = await fetch(`${API_BASE_URL}/api/ai/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: request.message,
          limit: 10,
          conversation_history: request.conversation_history || []
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const aiResponse = await response.json();
      
      // Convert AI response to ChatbotResponse format
      if (aiResponse.status === 'success') {
        let responseText = '';
        
        if (aiResponse.products && aiResponse.products.length > 0) {
          // Use agent_output from AI if available
          if (aiResponse.conversation_context && aiResponse.conversation_context.messages && aiResponse.conversation_context.messages.length > 0) {
            const latestMessage = aiResponse.conversation_context.messages[aiResponse.conversation_context.messages.length - 1];
            responseText = latestMessage.agent_output || `I found ${aiResponse.total_results || aiResponse.products.length} products for "${request.message}".`;
          } else {
            responseText = `I found ${aiResponse.total_results || aiResponse.products.length} products for "${request.message}".`;
          }
          
          // Add function and language info
          if (aiResponse.function_used) {
            const functionName = aiResponse.function_used === 'find_gifts' ? 'gift search' : 'product search';
            responseText += `\n\n🔍 Used: ${functionName}`;
          }
          if (aiResponse.language_detected) {
            responseText += ` (Language: ${aiResponse.language_detected})`;
          }
          
          // Add search intent info if available
          if (aiResponse.search_intent) {
            const intent = aiResponse.search_intent;
            const appliedFilters = [];
            if (intent.filters.category) appliedFilters.push(`Category: ${intent.filters.category}`);
            if (intent.filters.min_price || intent.filters.max_price) {
              const priceRange = [];
              if (intent.filters.min_price) priceRange.push(`min $${intent.filters.min_price}`);
              if (intent.filters.max_price) priceRange.push(`max $${intent.filters.max_price}`);
              appliedFilters.push(`Price: ${priceRange.join(', ')}`);
            }
            if (intent.filters.min_rating) appliedFilters.push(`Min rating: ${intent.filters.min_rating} stars`);
            if (intent.filters.min_discount) appliedFilters.push(`Min discount: ${intent.filters.min_discount}%`);
            if (appliedFilters.length > 0) responseText += `\n\nI detected these filters: ${appliedFilters.join(', ')}`;
          }
          
          responseText += `\n\nHere are the top results:`;
        } else {
          // Use agent_output from AI response directly instead of hard-coding
          if (aiResponse.conversation_context && aiResponse.conversation_context.messages && aiResponse.conversation_context.messages.length > 0) {
            const latestMessage = aiResponse.conversation_context.messages[aiResponse.conversation_context.messages.length - 1];
            responseText = latestMessage.agent_output || aiResponse.message || aiResponse.response || "I'm here to help you find products. What are you looking for?";
          } else {
            responseText = aiResponse.message || aiResponse.response || "I'm here to help you find products. What are you looking for?";
          }
          
          if (aiResponse.function_used) {
            const functionName = aiResponse.function_used === 'find_gifts' ? 'gift search' : 'product search';
            responseText += `\n\n🔍 Used: ${functionName}`;
          }
          if (aiResponse.language_detected) {
            responseText += ` (Language: ${aiResponse.language_detected})`;
          }
        }

        // Convert AI products to frontend Product format
        const products: Product[] = aiResponse.products ? aiResponse.products.map((product: any) => ({
          id: product.id,
          name: product.name,
          price: product.price,
          original_price: product.original_price,
          category: product.category,
          imageUrl: product.imageUrl,
          description: product.description || '',
          rating: product.rating,
          discount: product.discount
        })) : [];

        return {
          response: responseText,
          products: products,
          search_params: {
            function_used: aiResponse.function_used,
            language_detected: aiResponse.language_detected,
            search_intent: aiResponse.search_intent
          },
          smart_search_used: true,
          parsed_filters: aiResponse.search_intent?.filters || {},
          function_used: aiResponse.function_used,
          language_detected: aiResponse.language_detected,
          conversation_context: aiResponse.conversation_context,
          page_code: products.length > 0 ? 'products' : 'others'
        };
      } else {
        // Handle error response - use AI message directly
        return {
          response: aiResponse.message || aiResponse.response || 'I encountered an issue while processing your request. Please try again.',
          products: [],
          search_params: {},
          function_used: aiResponse.function_used,
          language_detected: aiResponse.language_detected,
          page_code: 'others'
        };
      }

    } catch (error) {
      console.error('Chatbot service error:', error);
      // Fallback response
      return {
        response: "I'm sorry, I'm having trouble processing your request right now. Please try again later.",
        products: [],
        search_params: {},
        page_code: 'others'
      };
    }
  },

  // Helper function to check if chatbot component is using this service
  async isProductSearchQuery(message: string): Promise<boolean> {
    // Always return true since we're using AI middleware to handle all queries
    return true;
  }
};
