import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faShoppingCart, faEye } from '@fortawesome/free-solid-svg-icons';
import { toast } from 'react-toastify';
import { Product } from '../../contexts/ShopContext';
import WishlistButton from '../WishlistButton/WishlistButton';

interface SimpleProductCardProps {
  product: Product;
  onAddToCart: (product: Product) => void;
  onAddToWishlist: (product: Product) => void;
  isInWishlist: (id: number) => boolean;
}

const SimpleProductCard: React.FC<SimpleProductCardProps> = ({ 
  product, 
  onAddToCart, 
  onAddToWishlist, 
  isInWishlist 
}) => {
  const [isHovered, setIsHovered] = useState(false);

  const styles = {
    simpleProductCard: {
      backgroundColor: 'white',
      borderRadius: '6px',
      boxShadow: isHovered ? '0 8px 20px rgba(0,0,0,0.12)' : '0 2px 6px rgba(0,0,0,0.08)',
      overflow: 'hidden',
      transition: 'transform 0.3s ease, box-shadow 0.3s ease',
      position: 'relative' as const,
      transform: isHovered ? 'translateY(-5px)' : 'translateY(0)'
    },
    productImageContainer: {
      position: 'relative' as const
    },
    productImage: {
      width: '75%',
      height: '220px',
      objectFit: 'cover' as const,
      display: 'block',
      margin: '0 auto'
    },
    productBadge: {
      position: 'absolute' as const,
      top: '1rem',
      padding: '0.3rem 0.6rem',
      borderRadius: '3px',
      fontSize: '0.7rem',
      fontWeight: 600,
      fontFamily: "'Open Sans', Arial, sans-serif",
      color: 'white'
    },
    productBadgeNew: {
      left: '1rem',
      backgroundColor: '#28a745',
      textTransform: 'uppercase' as const
    },
    productBadgeDiscount: {
      right: '1rem',
      backgroundColor: '#dc3545'
    },
    productOverlay: {
      position: 'absolute' as const,
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.6)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '1rem',
      opacity: isHovered ? 1 : 0,
      visibility: isHovered ? 'visible' as const : 'hidden' as const,
      transition: 'all 0.3s ease'
    },
    overlayButton: {
      backgroundColor: '#2ecc71',
      color: 'white',
      border: 'none',
      borderRadius: '50%',
      width: '45px',
      height: '45px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      cursor: 'pointer',
      fontSize: '1.2rem',
      transition: 'all 0.3s ease',
      textDecoration: 'none'
    },
    productInfo: {
      padding: '1rem',
      position: 'relative' as const
    },
    productTitle: {
      fontSize: '0.9rem',
      marginBottom: '0.5rem',
      color: '#2c3e50',
      lineHeight: 1.3,
      height: '2.6rem',
      overflow: 'hidden',
      fontFamily: "'Open Sans', Arial, sans-serif",
      fontWeight: 400
    },
    priceAndActions: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: '0.5rem'
    },
    priceContainer: {
      display: 'flex',
      flexDirection: 'column' as const
    },
    original_price: {
      fontSize: '0.8rem',
      color: '#999',
      textDecoration: 'line-through',
      fontFamily: "'Open Sans', Arial, sans-serif",
      display: 'block'
    },
    currentPrice: {
      fontSize: '1.1rem',
      fontWeight: 600,
      color: '#e74c3c',
      fontFamily: "'Open Sans', Arial, sans-serif"
    },
    actionButtons: {
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem'
    },
    actionButton: {
      border: 'none',
      borderRadius: '50%',
      width: '35px',
      height: '35px',
      cursor: 'pointer',
      fontSize: '1rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      transition: 'all 0.3s ease',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    },
    wishlistButton: {
      backgroundColor: isInWishlist(product.id) ? '#dc3545' : 'rgba(255,255,255,0.9)',
      color: isInWishlist(product.id) ? 'white' : '#333'
    },
    cartButton: {
      backgroundColor: '#fed700',
      color: '#fff',
      fontSize: '0.9rem'
    },
    productLink: {
      display: 'block',
      textDecoration: 'none'
    },
    productTitleLink: {
      color: 'inherit',
      textDecoration: 'none',
      transition: 'color 0.3s ease'
    }
  };

  return (
    <div 
      style={styles.simpleProductCard}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Product Image */}
      <div style={styles.productImageContainer}>
        <Link to={`/product/${product.id}`} style={styles.productLink}>
          <img
            src={product.imageUrl}
            alt={product.name}
            style={styles.productImage}
          />
        </Link>
        
        {/* Product Badges */}
        {product.isNew && (
          <span style={{...styles.productBadge, ...styles.productBadgeNew}}>
            NEW
          </span>
        )}
        
   
        {/* Hover Overlay with Action Buttons */}
        <div style={styles.productOverlay}>
          <Link 
            to={`/product/${product.id}`}
            style={styles.overlayButton}
            title="Quick View"
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = '#27ae60';
              e.currentTarget.style.transform = 'scale(1.1)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = '#2ecc71';
              e.currentTarget.style.transform = 'scale(1)';
            }}
          >
            <FontAwesomeIcon icon={faEye} />
          </Link>
        </div>
      </div>

      {/* Product Info */}
      <div style={styles.productInfo}>
        <h3 style={styles.productTitle}>
          <Link 
            to={`/product/${product.id}`} 
            style={styles.productTitleLink}
            onMouseOver={(e) => {
              e.currentTarget.style.color = '#ff6b35';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.color = 'inherit';
            }}
          >
            {product.name}
          </Link>
        </h3>

        {/* Price and Cart Icon */}
        <div style={styles.priceAndActions}>
          <div style={styles.priceContainer}>
            {product.original_price && (
              <span style={styles.original_price}>
                ${product.original_price}
              </span>
            )}
            <span style={styles.currentPrice}>
              ${product.price}
            </span>
          </div>

          {/* Action Buttons Container */}
          <div style={styles.actionButtons} className="thangnaozay">
            {/* Wishlist Button with Modal */}
            <WishlistButton 
              productId={product.id}
              className="card-wishlist"
              onWishlistChange={(inWishlist: boolean) => {
                // Optional: Update parent component state if needed
                console.log(`Product ${product.id} wishlist status:`, inWishlist);
              }}
            />

            {/* Add to Cart Button */}
            <button
              onClick={() => {
                onAddToCart(product);
                // Add toast notification for add to cart
                toast.success(`🛒 "${product.name}" added to cart!`, {
                  position: "top-right",
                  autoClose: 3000,
                  hideProgressBar: false,
                  closeOnClick: true,
                  pauseOnHover: true,
                  draggable: true,
                });
              }}
              style={{...styles.actionButton, ...styles.cartButton}}
              title="Add to Cart"
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = '#e6c200';
                e.currentTarget.style.transform = 'scale(1.1)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = '#fed700';
                e.currentTarget.style.transform = 'scale(1)';
              }}
            >
              <FontAwesomeIcon icon={faShoppingCart} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimpleProductCard;
