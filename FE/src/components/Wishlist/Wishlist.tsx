import React, { useState, useEffect } from 'react';
import { useShop } from '../../contexts/ShopContext';
import { useToast } from '../../contexts/ToastContext';
import { Link } from 'react-router-dom';
import SimpleProductCard from '../SimpleProductCard';

const Wishlist = () => {
  const { state, removeFromWishlist, addToCart } = useShop();
  const wishlist = state.wishlist;
  const { showSuccess } = useToast();

  // Responsive state
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Inline styles
  const styles = {
    wishlistContainer: {
      maxWidth: '1200px',
      margin: '2rem auto',
      padding: isMobile ? '1rem' : '2rem'
    },
    wishlistTitle: {
      fontSize: '2rem',
      fontWeight: 'bold',
      marginBottom: '2rem',
      color: '#1f2937',
      textAlign: 'center' as const
    },
    wishlistEmptyContainer: {
      textAlign: 'center' as const,
      padding: '3rem',
      backgroundColor: '#f9fafb',
      borderRadius: '8px',
      border: '2px dashed #d1d5db'
    },
    wishlistEmptyTitle: {
      fontSize: '1.5rem',
      fontWeight: 'bold',
      color: '#374151',
      marginBottom: '1rem'
    },
    wishlistEmptyText: {
      color: '#6b7280',
      fontSize: '1.125rem',
      marginBottom: '2rem'
    },
    wishlistButtonPrimary: {
      backgroundColor: '#3b82f6',
      color: 'white',
      padding: '0.75rem 1.5rem',
      borderRadius: '8px',
      textDecoration: 'none',
      display: 'inline-block',
      fontWeight: '600',
      transition: 'background-color 0.2s ease'
    },
    wishlistButtonSecondary: {
      backgroundColor: '#6b7280',
      color: 'white',
      padding: '0.75rem 1.5rem',
      borderRadius: '8px',
      textDecoration: 'none',
      display: 'inline-block',
      fontWeight: '600',
      transition: 'background-color 0.2s ease'
    },
    wishlistGrid: {
      display: 'grid',
      gridTemplateColumns: isMobile ? 'repeat(auto-fill, minmax(200px, 1fr))' : 'repeat(auto-fill, minmax(250px, 1fr))',
      gap: isMobile ? '1rem' : '2rem',
      marginBottom: '2rem'
    },
    wishlistContinueSection: {
      textAlign: 'center' as const,
      marginTop: '2rem'
    }
  };

  if (wishlist.length === 0) {
    return (
      <div style={styles.wishlistEmptyContainer}>
        <h2 style={styles.wishlistEmptyTitle}>
          Your Wishlist is Empty
        </h2>
        <p style={styles.wishlistEmptyText}>
          Save items you love for later!
        </p>
        <Link
          to="/products"
          style={styles.wishlistButtonPrimary}
          onMouseOver={(e) => {
            e.currentTarget.style.backgroundColor = '#2563eb';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.backgroundColor = '#3b82f6';
          }}
        >
          Continue Shopping
        </Link>
      </div>
    );
  }

  const handleAddToCart = (product: any) => {
    addToCart(product);
    showSuccess(`Added to Cart!`, `${product.name} has been added to your cart.`);
  };

  return (
    <div style={styles.wishlistContainer}>
      <h1 style={styles.wishlistTitle}>
        My Wishlist
      </h1>

      <div style={styles.wishlistGrid}>
        {wishlist.map((product) => (
          <SimpleProductCard
            key={product.id}
            product={product}
            onAddToCart={handleAddToCart}
          />
        ))}
      </div>

      <div style={styles.wishlistContinueSection}>
        <Link
          to="/products"
          style={styles.wishlistButtonSecondary}
          onMouseOver={(e) => {
            e.currentTarget.style.backgroundColor = '#4b5563';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.backgroundColor = '#6b7280';
          }}
        >
          Continue Shopping
        </Link>
      </div>
    </div>
  );
};

export default Wishlist;
