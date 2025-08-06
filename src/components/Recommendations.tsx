import React from 'react';
import { useRecommendations } from '../hooks/useRecommendations';
import SimpleProductCard from './SimpleProductCard';
import { useShop } from '../contexts/ShopContext';
import { useAuth } from '../contexts/AuthContext';
import { Product } from '../contexts/ShopContext';

interface RecommendationsProps {
  limit?: number;
  title?: string;
  className?: string;
}

const Recommendations: React.FC<RecommendationsProps> = ({ 
  limit = 8, 
  title = "Recommended for You",
  className = ""
}) => {
  const { recommendations, loading, error, isPersonalized } = useRecommendations(limit);
  const { addToCart, addToWishlist, isInWishlist } = useShop();
  const { currentUser } = useAuth();

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

  const displayTitle = isPersonalized && currentUser
    ? `${title} (Personalized)`
    : title;

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
        {recommendations.map((product: Product) => {
          return (
              <SimpleProductCard
                key={product.id}
                product={product}
                onAddToCart={() => addToCart(product)}
                onAddToWishlist={() => addToWishlist(product)}
                isInWishlist={isInWishlist}
              />
          );
        })}
      </div>
    </div>
  );
};

export default Recommendations;
