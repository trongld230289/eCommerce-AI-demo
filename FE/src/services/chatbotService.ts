import { Product } from '../contexts/ShopContext';

<<<<<<< HEAD
const API_BASE_URL = 'http://localhost:8000';
=======
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface ConversationMessage {
  role: string; // "user" or "assistant"
  content: string;
}
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e

export interface ChatbotRequest {
  message: string;
  user_id?: string;
<<<<<<< HEAD
=======
  conversation_history?: ConversationMessage[];
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
}

export interface ChatbotResponse {
  response: string;
  products: Product[];
  search_params: Record<string, any>;
  redirect_url?: string;
  page_code?: string;
  smart_search_used?: boolean;
  parsed_filters?: Record<string, any>;
<<<<<<< HEAD
}

export interface SmartSearchRequest {
  query: string;
  limit?: number;
}

export interface SmartSearchResponse {
  query: string;
  results: Product[];
  parsed_filters: Record<string, any>;
  total_found: number;
  search_type: string;
  timestamp: string;
}

export interface SemanticSearchRequest {
  query: string;
  limit?: number;
  min_similarity?: number;
}

export interface SemanticSearchResponse {
  query: string;
  results: Product[];
  search_type: string;
  total_found: number;
  min_similarity: number;
  timestamp: string;
}

export interface HybridSearchRequest {
  query: string;
  limit?: number;
  semantic_weight?: number;
}

export interface HybridSearchResponse {
  query: string;
  results: Product[];
  search_type: string;
  total_found: number;
  semantic_weight: number;
  timestamp: string;
=======
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
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
}

export const chatbotService = {
  async sendMessage(request: ChatbotRequest): Promise<ChatbotResponse> {
    try {
<<<<<<< HEAD
      // Check if the message looks like a product search query
      const isProductSearchQuery = true; //= await chatbotService.isProductSearchQuery(request.message);
      
      if (isProductSearchQuery) {
        // Try semantic search first for better results
        let searchResult: SemanticSearchResponse | HybridSearchResponse = await chatbotService.performSemanticSearch({
          query: request.message,
          limit: 10,
          min_similarity: 0.2 // Lower threshold for more results
        });

        // If semantic search doesn't return enough results, try hybrid search
        if (searchResult.results.length < 3) {
          const hybridResult = await chatbotService.performHybridSearch({
            query: request.message,
            limit: 2,
            semantic_weight: 0.6 // Balanced approach
          });
          
          if (hybridResult.results.length > searchResult.results.length) {
            searchResult = hybridResult;
          }
        }

        // If still no good results, fallback to smart search
        // if (searchResult.results.length === 0) {
        //   const smartResult = await chatbotService.performSmartSearch({
        //     query: request.message,
        //     limit: 10
        //   });
          
        //   if (smartResult.results.length > 0) {
        //     return {
        //       response: `I found ${smartResult.total_found} products using smart search for "${request.message}". Here are the results:`,
        //       products: smartResult.results,
        //       search_params: smartResult.parsed_filters,
        //       smart_search_used: true,
        //       parsed_filters: smartResult.parsed_filters,
        //       page_code: 'products'
        //     };
        //   }
        // }

        if (searchResult.results.length > 0) {
          const searchType = searchResult.search_type.includes('semantic') ? 'semantic' : 
                            searchResult.search_type.includes('hybrid') ? 'hybrid' : 'smart';
          
          return {
            response: `I found ${searchResult.total_found} products using ${searchType} search for "${request.message}". Here are the best matches:`,
            products: searchResult.results,
            search_params: { search_type: searchResult.search_type },
            smart_search_used: true,
            parsed_filters: { search_type: searchResult.search_type },
            page_code: 'products'
          };
        } else {
          return {
            response: `I couldn't find any products matching "${request.message}". Try searching for laptops, phones, headphones, or other electronics.`,
            products: [],
            search_params: {},
            smart_search_used: true,
            page_code: 'others'
          };
        }
      }

      // For non-product queries, provide helpful responses
      const message = request.message.toLowerCase();
      let response = "Hello! I'm here to help you find products. What are you looking for?";
      
      if (message.includes('hello') || message.includes('hi')) {
        response = "Hello! I can help you find laptops, phones, headphones, and other electronics. What are you looking for?";
      } else if (message.includes('help')) {
        response = "I can help you search for products! Try asking me things like 'I need a laptop' or 'show me headphones'.";
      } else if (message.includes('thank')) {
        response = "You're welcome! Is there anything else I can help you find?";
      } else {
        response = "I'm here to help you find products. Try searching for laptops, phones, headphones, or other electronics!";
      }

      return {
        response,
        products: [],
        search_params: {},
        page_code: 'others'
      };

=======
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

>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
    } catch (error) {
      console.error('Chatbot service error:', error);
      // Fallback response
      return {
        response: "I'm sorry, I'm having trouble processing your request right now. Please try again later.",
        products: [],
<<<<<<< HEAD
        search_params: {}
=======
        search_params: {},
        page_code: 'others'
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
      };
    }
  },

<<<<<<< HEAD
  // Check if a message is likely a product search query
  async isProductSearchQuery(message: string): Promise<boolean> {
    const searchKeywords = [
      'find', 'search', 'looking for', 'show me', 'want', 'need', 'buy', 'get',
      'laptop', 'phone', 'headphones', 'speaker', 'watch', 'mouse', 'keyboard',
      'electronics', 'accessories', 'under', 'below', 'above', 'cheap', 'expensive',
      'brand', 'price', 'dell', 'apple', 'samsung', 'sony', 'hp', 'lenovo',
      'product', 'item', 'device', 'gadget'
    ];

    const lowerMessage = message.toLowerCase();
    return searchKeywords.some(keyword => lowerMessage.includes(keyword));
  },

  // Perform smart search using the backend API
  async performSmartSearch(request: SmartSearchRequest): Promise<SmartSearchResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/search/smart`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Smart search service error:', error);
      // Return empty results on error
      return {
        query: request.query,
        results: [],
        parsed_filters: {},
        total_found: 0,
        search_type: 'error',
        timestamp: new Date().toISOString()
      };
    }
  },

  // Perform semantic search using embeddings and cosine similarity
  async performSemanticSearch(request: SemanticSearchRequest): Promise<SemanticSearchResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/search/semantic`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Semantic search service error:', error);
      // Return empty results on error
      return {
        query: request.query,
        results: [],
        total_found: 0,
        search_type: 'semantic_error',
        min_similarity: request.min_similarity || 0.3,
        timestamp: new Date().toISOString()
      };
    }
  },

  // Perform hybrid search combining semantic and keyword matching
  async performHybridSearch(request: HybridSearchRequest): Promise<HybridSearchResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/search/hybrid`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Hybrid search service error:', error);
      // Return empty results on error
      return {
        query: request.query,
        results: [],
        total_found: 0,
        search_type: 'hybrid_error',
        semantic_weight: request.semantic_weight || 0.7,
        timestamp: new Date().toISOString()
      };
    }
=======
  // Helper function to check if chatbot component is using this service
  async isProductSearchQuery(message: string): Promise<boolean> {
    // Always return true since we're using AI middleware to handle all queries
    return true;
>>>>>>> 152c40476bd97e5141c23051b72efd7a3226cb7e
  }
};
