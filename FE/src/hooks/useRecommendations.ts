import { useState, useEffect, useCallback } from 'react';
import { recommendationService, UserEvent } from '../services/recommendationService';
import { Product } from '../contexts/ShopContext';
import { useAuth } from '../contexts/AuthContext';

export const useRecommendations = (limit: number = 10) => {
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
      console.log('Fetching recommendations for userId:', userId); // Debug log
      
      const result = await recommendationService.getRecommendations(userId, limit);
      
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
        const fallbackProducts = await recommendationService.getAllProducts();
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
  const trackUserEvent = useCallback(async (eventType: UserEvent['event_type'], productId: string | number) => {
    if (!currentUser?.uid) return false;
    
    try {
      const eventData: UserEvent = {
        user_id: currentUser.uid,
        event_type: eventType,
        product_id: productId,
        session_id: `session_${Date.now()}`, // Simple session ID
        metadata: {
          timestamp: new Date().toISOString(),
          source: 'frontend_recommendations'
        }
      };
      
      const success = await recommendationService.trackUserEvent(eventData);
      if (success) {
        console.log(`✅ Tracked ${eventType} event for product ${productId}`);
        // Optionally refresh recommendations after certain events
        if (eventType === 'add_to_cart' || eventType === 'add_to_wishlist') {
          setTimeout(() => fetchRecommendations(), 1000); // Refresh after 1 second
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
    trackEvent: trackUserEvent
  };
};

export const useAllProducts = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProducts = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await recommendationService.getAllProducts();
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
};
