import React, { useState, useEffect, useRef, useCallback } from 'react';
import { wishlistRecommendationsService } from '../../services/wishlistRecommendationsService';
import { useAuth } from '../../contexts/AuthContext';

// Simple test component to test enhanced API with performance monitoring
const WishlistRecommendationTest: React.FC = () => {
  const { currentUser } = useAuth();
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [apiCallCount, setApiCallCount] = useState(0);
  const [lastApiCallTime, setLastApiCallTime] = useState<string>('');
  const hasCalledApi = useRef(false); // Prevent duplicate API calls

  const testEnhancedAPI = useCallback(async () => {
    // Prevent multiple API calls
    if (hasCalledApi.current) {
      console.log('⚠️ API already called once, using cached results');
      return;
    }

    setLoading(true);
    setError('');
    const startTime = performance.now();
    
    try {
      // Simulate multiple wishlist tabs with product IDs (including duplicates)
      const tab1Products = [6, 7, 8]; // Electronics
      const tab2Products = [6, 9, 10]; // Favorites (6 is duplicate)
      const tab3Products = [11, 12]; // Gift ideas
      
      // Combine all product IDs (API will handle deduplication and optimization)
      const allProductIds = [...tab1Products, ...tab2Products, ...tab3Products];
      
      console.log('🚀 Testing enhanced single product API with product IDs:', allProductIds);
      console.log('📊 Unique products:', Array.from(new Set(allProductIds)));
      console.log('👤 Current user ID:', currentUser?.uid || 'No user logged in');
      
      // Call new single product API for each product individually (in parallel)
      const recommendationMap = await wishlistRecommendationsService.getSingleProductRecommendations(allProductIds, currentUser?.uid);
      
      // Convert map to array for display
      const recommendationArray = Array.from(recommendationMap.values());
      
      const endTime = performance.now();
      const duration = Math.round(endTime - startTime);
      
      setRecommendations(recommendationArray);
      setApiCallCount(prev => prev + 1);
      setLastApiCallTime(new Date().toLocaleTimeString());
      hasCalledApi.current = true; // Mark as called to prevent future calls
      
      console.log(`✅ Single Product API Response (${duration}ms):`, recommendationArray);
      console.log(`🎯 Performance: Individual API calls handled ${allProductIds.length} products (${Array.from(new Set(allProductIds)).length} unique)`);
      console.log(`📊 Recommendations received: ${recommendationArray.length}`);
      
    } catch (err) {
      console.error('❌ Error testing enhanced API:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [currentUser]); // useCallback dependency on currentUser

  useEffect(() => {
    // Only call the API when user is available
    if (currentUser) {
      testEnhancedAPI();
    }
  }, [currentUser, testEnhancedAPI]); // Depend on currentUser and testEnhancedAPI

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h2>🚀 Individual Product API Test</h2>
      
      {/* Performance Stats */}
      <div style={{ 
        backgroundColor: '#e0f2fe', 
        padding: '1rem', 
        borderRadius: '8px', 
        marginBottom: '1rem',
        border: '1px solid #0277bd'
      }}>
        <h4 style={{ margin: '0 0 0.5rem 0' }}>📊 Performance Stats</h4>
        <p style={{ margin: '0.25rem 0' }}>🔢 API Sessions: {apiCallCount}</p>
        <p style={{ margin: '0.25rem 0' }}>⏰ Last Call: {lastApiCallTime || 'Not yet called'}</p>
        <p style={{ margin: '0.25rem 0' }}>🎯 Individual Calls: {hasCalledApi.current ? '✅ Completed' : '⏳ Ready'}</p>
      </div>
      
      <div style={{ marginBottom: '1rem' }}>
        <button 
          onClick={testEnhancedAPI} 
          disabled={loading}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Loading...' : 'Test Individual Product API'}
        </button>
      </div>
      
      {error && (
        <div style={{ 
          padding: '1rem', 
          backgroundColor: '#fee2e2', 
          color: '#dc2626', 
          borderRadius: '8px',
          marginBottom: '1rem'
        }}>
          <strong>Error:</strong> {error}
        </div>
      )}
      
      <div style={{ backgroundColor: '#f8fafc', padding: '1rem', borderRadius: '8px' }}>
        <h3>Results ({recommendations.length} recommendations)</h3>
        
        {recommendations.length > 0 ? (
          <div style={{ display: 'grid', gap: '1rem' }}>
            {recommendations.map((rec, index) => (
              <div key={index} style={{ 
                backgroundColor: 'white', 
                padding: '1rem', 
                borderRadius: '8px',
                border: '1px solid #e5e7eb'
              }}>
                <div style={{ marginBottom: '0.5rem' }}>
                  <strong>Product Query ID:</strong> {rec.product_query_id}
                </div>
                <div style={{ marginBottom: '0.5rem', fontStyle: 'italic' }}>
                  "{rec.suggestion}"
                </div>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                  <img 
                    src={rec.product_suggestion.imageUrl} 
                    alt={rec.product_suggestion.name}
                    style={{ width: '60px', height: '60px', objectFit: 'cover', borderRadius: '4px' }}
                  />
                  <div>
                    <div><strong>{rec.product_suggestion.name}</strong></div>
                    <div style={{ color: '#059669' }}>
                      ${rec.product_suggestion.price}
                      {rec.product_suggestion.original_price && (
                        <span style={{ color: '#6b7280', textDecoration: 'line-through', marginLeft: '0.5rem' }}>
                          ${rec.product_suggestion.original_price}
                        </span>
                      )}
                    </div>
                    <div style={{ color: '#6b7280', fontSize: '0.9rem' }}>
                      {rec.product_suggestion.category}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          !loading && <p>No recommendations found.</p>
        )}
      </div>
      
      <div style={{ marginTop: '2rem', fontSize: '0.9rem', color: '#6b7280' }}>
        <h4>🔧 Individual Product API Features:</h4>
        <ul>
          <li>✅ Individual API call per product</li>
          <li>✅ Parallel processing for faster response</li>
          <li>✅ Better granular control</li>
          <li>✅ Async API with optimized performance</li>
          <li>✅ Exclude current user's shared wishlists</li>
          <li>✅ Avoid self-recommendations</li>
          <li>✅ Single product endpoint: <code>/api/wishlist/recommendation/single</code></li>
        </ul>
      </div>
    </div>
  );
};

export default WishlistRecommendationTest;
