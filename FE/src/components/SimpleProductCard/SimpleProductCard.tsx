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
}

const SimpleProductCard: React.FC<SimpleProductCardProps> = ({ 
  product, 
  onAddToCart
}) => {
  const [isHovered, setIsHovered] = useState(false);

  // Function to get icon and title based on rec_source
  const getRecommendationIcon = (source: string) => {
    switch (source) {
      case 'personalized':
        return { icon: '👤', title: 'Personalized Recommendation', animation: 'personalizedPulse' };
      case 'category':
        return { icon: '📂', title: 'Category Based', animation: 'categoryBounce' };
      case 'trending':
        return { icon: '🔥', title: 'Trending Product', animation: 'trendingFlame' };
      case 'rating':
        return { icon: '⭐', title: 'Top Rated', animation: 'ratingSpark' };
      case 'description':
        return { icon: '📝', title: 'Description Match', animation: 'descriptionWrite' };
      case 'wishlist':
        return { icon: '💖', title: 'Wishlist Suggestion', animation: 'wishlistHeart' };
      case 'purchase':
        return { icon: '🛒', title: 'Purchase History Based', animation: 'purchaseShake' };
      case 'same_taste':
        return { icon: '🤝', title: 'Similar Taste', animation: 'tasteMate' };
      case 'product':
        return { icon: '🛍️', title: 'Similarity Product', animation: 'productPulse' };
      case 'gift':
        return { icon: '🎁', title: 'Gift Suggestion', animation: 'giftGlow' };
      default:
        return null;
    }
  };

    // Get recommendation data if rec_source exists
  const recommendationData = product.rec_source ? getRecommendationIcon(product.rec_source) : null;
  
  // Debug log
  console.log('Product rec_source:', product.rec_source, 'recommendationData:', recommendationData);

  const styles = {
    simpleProductCard: {
      backgroundColor: 'white',
      borderRadius: '6px',
      boxShadow: isHovered ? '0 8px 20px rgba(0,0,0,0.12)' : '0 2px 6px rgba(0,0,0,0.08)',
      overflow: 'visible', // Fix icon bị đè
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
        {product.discount && product.discount > 0 && (
          <span style={{...styles.productBadge, ...styles.productBadgeNew}}>
            -{product.discount}%
          </span>
        )}
        
        {/* Recommendation icon based on rec_source */}
        {recommendationData && (
          <div 
            title={recommendationData.title}
            style={{
              position: 'absolute',
              top: '-10px',
              right: '-10px',
              zIndex: 99,
              background: '#fff',
              borderRadius: '50%',
              width: '28px',
              height: '28px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.18)',
              border: '2.5px solid #fff',
              cursor: 'help',
              transition: 'transform 0.2s ease, box-shadow 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'scale(1.1)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.25)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.18)';
            }}
          >
            <span 
              style={{ 
                fontSize: '15px', 
                display: 'block',
                animation: `${recommendationData.animation} 2s ease-in-out infinite alternate`,
                pointerEvents: 'none'
              }}
            >
              {recommendationData.icon}
            </span>
          </div>
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
      
      {/* Add CSS animations */}
      <style>{`
        @keyframes personalizedPulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.2); }
        }
        @keyframes categoryBounce {
          0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
          40% { transform: translateY(-3px); }
          60% { transform: translateY(-1px); }
        }
        @keyframes trendingFlame {
          0% { transform: scale(1) rotate(0deg); }
          50% { transform: scale(1.1) rotate(2deg); }
          100% { transform: scale(1) rotate(0deg); }
        }
        @keyframes ratingStar {
          0%, 100% { transform: scale(1) rotate(0deg); }
          50% { transform: scale(1.2) rotate(180deg); }
        }
        @keyframes descriptionFloat {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-2px); }
        }
        @keyframes wishlistHeart {
          0%, 100% { transform: scale(1); color: #e74c3c; }
          50% { transform: scale(1.3); color: #c0392b; }
        }
        @keyframes purchaseShake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-1px); }
          75% { transform: translateX(1px); }
        }
        @keyframes sameTasteWave {
          0% { transform: translateX(0px); }
          50% { transform: translateX(2px); }
          100% { transform: translateX(0px); }
        }
        @keyframes productPulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }
        @keyframes giftGlow {
          0% { filter: brightness(1); }
          100% { filter: brightness(1.5) drop-shadow(0 0 5px gold); }
        }
      `}</style>
    </div>
  );
};

export default SimpleProductCard;
