import { useState, useEffect } from 'react';
import { recommendationService, convertApiProductToProduct } from '../services/recommendationService';
import { Product } from '../types';
import { useAuth } from '../contexts/AuthContext';

export const useRecommendations = (limit: number = 10) => {
  const [recommendations, setRecommendations] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPersonalized, setIsPersonalized] = useState(false);
  const { currentUser } = useAuth();

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const userId = currentUser?.uid;
      console.log('Fetching recommendations for userId:', userId); // Debug log
      const result = await recommendationService.getRecommendations(userId, limit);
      const convertedProducts = result.products.map(convertApiProductToProduct);
      setRecommendations(convertedProducts);
      setIsPersonalized(result.is_personalized);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch recommendations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, [currentUser?.uid, limit]);

  return {
    recommendations,
    loading,
    error,
    isPersonalized,
    refetch: fetchRecommendations
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
      const convertedProducts = result.map(convertApiProductToProduct);
      setProducts(convertedProducts);
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
