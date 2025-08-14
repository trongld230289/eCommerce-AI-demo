import { useState, useEffect, useCallback } from 'react';
import { Product } from '../contexts/ShopContext';
import { useAuth } from '../contexts/AuthContext';

// API endpoints
const API_BASE_URL = 'http://localhost:8000';

interface RecommendationResponse {
  recommendations?: Product[];
  products?: Product[];
  user_id: string | null;
  source?: string;
  count?: number;
  timestamp?: string;
}

interface UserEvent {
  user_id: string;
  event_type: 'view' | 'add_to_cart' | 'remove_from_cart' | 'add_to_wishlist' | 'remove_from_wishlist' | 'purchase';
  product_id: string | number;
  session_id?: string;
  metadata?: Record<string, any>;
}

// Simple recommendation service functions
const getRecommendations = async (userId?: string, limit: number = 10): Promise<RecommendationResponse> => {
  try {
    const url = userId 
      ? `${API_BASE_URL}/api/recommendations/${userId}?limit=${limit}`
      : `${API_BASE_URL}/api/recommendations?limit=${limit}`;
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    throw error;
  }
};

const getAllProducts = async (): Promise<Product[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/products`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data.products || [];
  } catch (error) {
    console.error('Error fetching products:', error);
    throw error;
  }
};

const trackUserEvent = async (eventData: UserEvent): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/recommendations/track`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(eventData),
    });
    
    return response.ok;
  } catch (error) {
    console.error('Error tracking user event:', error);
    return false;
  }
};

// Main hook function
function useRecommendations(limit: number = 10) {
  const [recommendations, setRecommendations] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPersonalized, setIsPersonalized] = useState(false);
  const [source, setSource] = useState<string>('unknown');
  const { currentUser } = useAuth();

  const fetchRecommendations = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const userId = currentUser?.uid;
      console.log('Fetching recommendations for userId:', userId);
      
      const result = await getRecommendations(userId, limit);
      
      // Extract products from either recommendations or products field
      const products = result.recommendations || result.products || [];
      setRecommendations(products);
      
      // Determine if personalized based on response data
      const personalized = Boolean(userId && result.source === 'recommendation_system');
      setIsPersonalized(personalized);
      setSource(result.source || 'unknown');
      
      console.log('Recommendations loaded:', {
        count: products.length,
        isPersonalized: personalized,
        source: result.source
      });
    } catch (err) {
      console.error('Failed to fetch recommendations:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch recommendations');
      
      // Fallback to get some products
      try {
        const fallbackProducts = await getAllProducts();
        setRecommendations(fallbackProducts.slice(0, limit));
        setIsPersonalized(false);
        setSource('fallback');
      } catch (fallbackErr) {
        console.error('Fallback also failed:', fallbackErr);
      }
    } finally {
      setLoading(false);
    }
  }, [currentUser?.uid, limit]);

  // Event tracking function
  const trackEvent = useCallback(async (eventType: UserEvent['event_type'], productId: string | number): Promise<boolean> => {
    if (!currentUser?.uid) return false;
    
    try {
      const eventData: UserEvent = {
        user_id: currentUser.uid,
        event_type: eventType,
        product_id: productId,
        session_id: `session_${Date.now()}`,
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'frontend_recommendations'
        }
      };
      
      const success = await trackUserEvent(eventData);
      if (success) {
        console.log(`✅ Tracked ${eventType} event for product ${productId}`);
        // Optionally refresh recommendations after certain events
        if (eventType === 'add_to_cart' || eventType === 'add_to_wishlist') {
          setTimeout(() => fetchRecommendations(), 1000);
        }
      }
      return success;
    } catch (error) {
      console.error('Error tracking user event:', error);
      return false;
    }
  }, [currentUser?.uid, fetchRecommendations]);

  useEffect(() => {
    fetchRecommendations();
  }, [fetchRecommendations]);

  return {
    recommendations,
    loading,
    error,
    isPersonalized,
    source,
    refetch: fetchRecommendations,
    trackEvent
  };
}

// Alternative hook
function useAllProducts() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProducts = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await getAllProducts();
      setProducts(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch products');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  return {
    products,
    loading,
    error,
    refetch: fetchProducts
  };
}

// Export using both methods to ensure compatibility
export { useRecommendations, useAllProducts };
export default useRecommendations;
