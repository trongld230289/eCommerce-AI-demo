import React from 'react';
import useRecommendations from '../hooks/useRecommendations';
import SimpleProductCard from './SimpleProductCard/SimpleProductCard';
import { useShop } from '../contexts/ShopContext';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { Product } from '../contexts/ShopContext';

interface RecommendationsProps {
  limit?: number;
  title?: string;
  className?: string;
}

const Recommendations: React.FC<RecommendationsProps> = ({ 
  limit = 3, 
  title = "Recommended for You",
  className = ""
}) => {
  const { recommendations, loading, error, isPersonalized, source, trackEvent } = useRecommendations(limit);
  const { addToCart } = useShop();
  const { showSuccess } = useToast();
  const { currentUser } = useAuth();

  // Enhanced cart handler with event tracking
  const handleAddToCart = async (product: Product) => {
    addToCart(product);
    showSuccess(`${product.name} added to cart!`, 'Check your cart to proceed to checkout.');
    
    // Track the add_to_cart event
    await trackEvent('add_to_cart', product.id);
  };

  // Track product view when user interacts with product card
  const handleProductView = async (product: Product) => {
    await trackEvent('view', product.id);
  };

  // Error state
  if (error) {
    return (
      <div className={`${className}`}>
        <h2 className="text-2xl font-bold mb-6">{title}</h2>
        <div className="text-center py-8 text-gray-500">
          <p>Unable to load recommendations at this time.</p>
          <p className="text-sm mt-2">Please try refreshing the page.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className={`${className}`}>
        <h2 className="text-2xl font-bold mb-6">{title}</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {Array.from({ length: limit }).map((_, index) => (
            <div key={index} className="animate-pulse">
              <div className="bg-gray-200 aspect-square rounded-lg mb-4"></div>
              <div className="h-4 bg-gray-200 rounded mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-6 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const displayTitle = (() => {
    if (isPersonalized && currentUser) {
      return `${title} (AI Personalized)`;
    } else if (source === 'recommendation_system') {
      return `${title} (Smart Recommendations)`;
    } else if (source === 'fallback') {
      return `${title} (Popular Products)`;
    }
    return title;
  })();

  // Safety check for recommendations
  const safeRecommendations = Array.isArray(recommendations) ? recommendations : [];

  return (
    <div className={`${className}`}>
      <div style={{ maxWidth: '1430px', margin: '0 auto', padding: '0 1rem' }}>
          <h2 style={{
            fontSize: '1.5rem',
            fontWeight: '600',
            color: '#2c3e50',
            textAlign: 'center',
            marginBottom: '2rem',
            fontFamily: 'Open Sans, Arial, sans-serif'
          }}>{displayTitle}</h2>

      </div>
      
      {/* Grid Layout - Same as Featured Products */}
      
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '2rem'
          }}>
        {safeRecommendations.length > 0 ? safeRecommendations.map((product: Product) => {
          return (
            <div 
              key={product.id}
              onClick={() => handleProductView(product)}
            >
              <SimpleProductCard
                product={product}
                onAddToCart={handleAddToCart}
              />
            </div>
          );
        }) : (
          <div style={{
            gridColumn: '1 / -1',
            textAlign: 'center',
            color: '#666',
            fontSize: '1.1rem',
            padding: '2rem'
          }}>
            No recommendations available at this time.
          </div>
        )}
      </div>
    </div>
  );
};

export default Recommendations;
