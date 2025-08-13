import React, { useState, useEffect } from 'react';
import { productApi } from '../../services/apiService';
import { Product } from '../../contexts/ShopContext';
import SimpleProductCard from '../SimpleProductCard';

interface FeaturedProductsProps {
  limit?: number;
  title?: string;
  onAddToCart?: (product: Product) => void;
  onAddToWishlist?: (product: Product) => void;
  isInWishlist?: (productId: number) => boolean;
}

const FeaturedProducts: React.FC<FeaturedProductsProps> = ({ 
  limit = 6,
  title = "Featured Products",
  onAddToCart,
  onAddToWishlist,
  isInWishlist
}) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    const fetchFeaturedProducts = async () => {
      try {
        setLoading(true);
        const featuredProducts = await productApi.getFeaturedProducts(limit);
        setProducts(featuredProducts);
        setError(null);
      } catch (err) {
        console.error('Error fetching featured products:', err);
        setError('Failed to load featured products');
      } finally {
        setLoading(false);
      }
    };

    fetchFeaturedProducts();
  }, [limit]);

  const styles = {
    section: {
      padding: '2rem 0',
      backgroundColor: '#ffffff',
    },
    container: {
      maxWidth: '1430px',
      margin: '0 auto',
      padding: '0 1rem',
    },
    header: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '2rem',
      flexDirection: isMobile ? 'column' as const : 'row' as const,
      gap: isMobile ? '1rem' : '0',
    },
    title: {
      fontSize: isMobile ? '1.8rem' : '2.2rem',
      fontWeight: 700,
      color: '#333',
      margin: 0,
      textAlign: isMobile ? 'center' as const : 'left' as const,
    },
    featuredBadge: {
      fontSize: '0.9rem',
      color: '#fff',
      backgroundColor: '#007bff',
      padding: '0.5rem 1rem',
      borderRadius: '20px',
      fontWeight: 600,
    },
    grid: {
      display: 'grid',
      gridTemplateColumns: isMobile 
        ? '1fr' 
        : `repeat(auto-fit, minmax(280px, 1fr))`,
      gap: '1.5rem',
      alignItems: 'start',
    },
    loadingContainer: {
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '200px',
    },
    loading: {
      fontSize: '1.1rem',
      color: '#666',
    },
    errorContainer: {
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '200px',
      backgroundColor: '#f8d7da',
      borderRadius: '8px',
      margin: '1rem 0',
    },
    error: {
      fontSize: '1.1rem',
      color: '#721c24',
    },
    noProducts: {
      textAlign: 'center' as const,
      color: '#666',
      fontSize: '1.1rem',
      padding: '2rem',
    },
    featuredStarBadge: {
      position: 'absolute' as const,
      top: '10px',
      left: '10px',
      backgroundColor: '#ffd700',
      color: '#333',
      padding: '0.25rem 0.5rem',
      borderRadius: '12px',
      fontSize: '0.75rem',
      fontWeight: 600,
      zIndex: 10,
      display: 'flex',
      alignItems: 'center',
      gap: '0.25rem',
    }
  };

  if (loading) {
    return (
      <div style={styles.section}>
        <div style={styles.container}>
          <div style={styles.loadingContainer}>
            <div style={styles.loading}>Loading featured products...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.section}>
        <div style={styles.container}>
          <div style={styles.errorContainer}>
            <div style={styles.error}>{error}</div>
          </div>
        </div>
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div style={styles.section}>
        <div style={styles.container}>
          <div style={styles.noProducts}>No featured products available.</div>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.section}>
      <div style={styles.container}>
        <div style={styles.header}>
          <h2 style={styles.title}>{title}</h2>
          <div style={styles.featuredBadge}>
            ⭐ Editor's Choice
          </div>
        </div>
        
        <div style={styles.grid}>
          {products.map((product) => (
            <div key={product.id} style={{ position: 'relative' }}>
              {/* Featured star badge */}
              <div style={styles.featuredStarBadge}>
                ⭐ Featured
              </div>
              <SimpleProductCard
                product={product}
                onAddToCart={onAddToCart || (() => {})}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FeaturedProducts;
