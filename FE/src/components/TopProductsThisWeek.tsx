import React, { useState, useEffect } from 'react';
import { productApi } from '../services/apiService';
import { Product } from '../contexts/ShopContext';
import SimpleProductCard from './SimpleProductCard';

interface TopProductsThisWeekProps {
  limit?: number;
  title?: string;
  onAddToCart?: (product: Product) => void;
}

const TopProductsThisWeek: React.FC<TopProductsThisWeekProps> = ({ 
  limit = 6,
  title = "Top Products This Week",
  onAddToCart
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
    const fetchTopProducts = async () => {
      try {
        setLoading(true);
        const topProducts = await productApi.getTopProductsThisWeek(limit);
        setProducts(topProducts);
        setError(null);
      } catch (err) {
        console.error('Error fetching top products:', err);
        setError('Failed to load top products');
      } finally {
        setLoading(false);
      }
    };

    fetchTopProducts();
  }, [limit]);

  const styles = {
    section: {
      padding: '2rem 0',
      backgroundColor: '#f8f9fa',
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
    weekPeriod: {
      fontSize: '0.9rem',
      color: '#666',
      backgroundColor: '#fff',
      padding: '0.5rem 1rem',
      borderRadius: '20px',
      border: '2px solid #e9ecef',
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
    popularityBadge: {
      position: 'absolute' as const,
      top: '10px',
      right: '10px',
      backgroundColor: '#ff6b6b',
      color: 'white',
      padding: '0.25rem 0.5rem',
      borderRadius: '12px',
      fontSize: '0.75rem',
      fontWeight: 600,
      zIndex: 10,
    }
  };

  const getCurrentWeekPeriod = () => {
    const now = new Date();
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    return `${weekAgo.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${now.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
  };

  if (loading) {
    return (
      <div style={styles.section}>
        <div style={styles.container}>
          <div style={styles.loadingContainer}>
            <div style={styles.loading}>Loading top products...</div>
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
          <div style={styles.noProducts}>No top products available this week.</div>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.section}>
      <div style={styles.container}>
        <div style={styles.header}>
          <h2 style={styles.title}>{title}</h2>
          <div style={styles.weekPeriod}>
            📊 {getCurrentWeekPeriod()}
          </div>
        </div>
        
        <div style={styles.grid}>
          {products.map((product) => (
            <div key={product.id} style={{ position: 'relative' }}>
              {/* Popularity ranking badge */}
              <div style={styles.popularityBadge}>
                #{products.indexOf(product) + 1}
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

export default TopProductsThisWeek;
