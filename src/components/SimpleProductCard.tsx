import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faShoppingCart, faEye, faHeart } from '@fortawesome/free-solid-svg-icons';
import { Product } from '../contexts/ShopContext';

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
  return (
    <div
      style={{
        backgroundColor: 'white',
        borderRadius: '6px',
        boxShadow: '0 2px 6px rgba(0,0,0,0.08)',
        overflow: 'hidden',
        transition: 'transform 0.3s ease, box-shadow 0.3s ease',
        position: 'relative'
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.transform = 'translateY(-5px)';
        e.currentTarget.style.boxShadow = '0 8px 20px rgba(0,0,0,0.12)';
        // Show overlay
        const overlay = e.currentTarget.querySelector(`.product-overlay-${product.id}`) as HTMLElement;
        if (overlay) {
          overlay.style.opacity = '1';
          overlay.style.visibility = 'visible';
        }
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 2px 6px rgba(0,0,0,0.08)';
        // Hide overlay
        const overlay = e.currentTarget.querySelector(`.product-overlay-${product.id}`) as HTMLElement;
        if (overlay) {
          overlay.style.opacity = '0';
          overlay.style.visibility = 'hidden';
        }
      }}
    >
      {/* Product Image */}
      <div style={{ position: 'relative' }}>
        <img
          src={product.image}
          alt={product.name}
          style={{
            width: '75%',
            height: '220px',
            objectFit: 'cover',
            display: 'block',
            margin: '0 auto'
          }}
        />
        
        {/* Product Badges */}
        {product.isNew && (
          <span style={{
            position: 'absolute',
            top: '1rem',
            left: '1rem',
            backgroundColor: '#28a745',
            color: 'white',
            padding: '0.3rem 0.6rem',
            borderRadius: '3px',
            fontSize: '0.7rem',
            fontWeight: '600',
            textTransform: 'uppercase',
            fontFamily: 'Open Sans, Arial, sans-serif'
          }}>
            NEW
          </span>
        )}
        
        {product.discount && (
          <span style={{
            position: 'absolute',
            top: '1rem',
            right: '1rem',
            backgroundColor: '#dc3545',
            color: 'white',
            padding: '0.3rem 0.6rem',
            borderRadius: '3px',
            fontSize: '0.7rem',
            fontWeight: '600',
            fontFamily: 'Open Sans, Arial, sans-serif'
          }}>
            -${product.discount}
          </span>
        )}

        {/* Hover Overlay with Action Buttons */}
        <div 
          className={`product-overlay-${product.id}`}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1rem',
            opacity: 0,
            visibility: 'hidden',
            transition: 'all 0.3s ease'
          }}
        >
          
          <button style={{
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
            transition: 'all 0.3s ease'
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.backgroundColor = '#27ae60';
            e.currentTarget.style.transform = 'scale(1.1)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.backgroundColor = '#2ecc71';
            e.currentTarget.style.transform = 'scale(1)';
          }}
          title="Quick View">
            <FontAwesomeIcon icon={faEye} />
          </button>
        </div>

       
      </div>

      {/* Product Info - Simplified */}
      <div style={{ padding: '1rem', position: 'relative' }}>
        <h3 style={{
          fontSize: '0.9rem',
          marginBottom: '0.5rem',
          color: '#2c3e50',
          lineHeight: '1.3',
          height: '2.6rem',
          overflow: 'hidden',
          fontFamily: 'Open Sans, Arial, sans-serif',
          fontWeight: '400'
        }}>
          {product.name}
        </h3>

        {/* Price and Cart Icon */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '0.5rem'
        }}>
          <div>
            {product.originalPrice && (
              <span style={{
                fontSize: '0.8rem',
                color: '#999',
                textDecoration: 'line-through',
                fontFamily: 'Open Sans, Arial, sans-serif',
                display: 'block'
              }}>
                ${product.originalPrice}
              </span>
            )}
            <span style={{
              fontSize: '1.1rem',
              fontWeight: '600',
              color: '#e74c3c',
              fontFamily: 'Open Sans, Arial, sans-serif'
            }}>
              ${product.price}
            </span>
          </div>

          {/* Action Buttons Container */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
             {/* Wishlist Button */}
            <button
              onClick={() => onAddToWishlist(product)}
              style={{
                backgroundColor: isInWishlist(product.id) ? '#dc3545' : 'rgba(255,255,255,0.9)',
                color: isInWishlist(product.id) ? 'white' : '#333',
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
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'scale(1.1)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'scale(1)';
              }}
              title="Add to Wishlist"
            >
              <FontAwesomeIcon 
                icon={faHeart} 
                style={{ 
                  color: isInWishlist(product.id) ? '#fff' : '#999' 
                }} 
              />
            </button>
            {/* Add to Cart Icon */}
            <button
              onClick={() => onAddToCart(product)}
              style={{
                backgroundColor: '#fed700',
                color: '#fff',
                border: 'none',
                borderRadius: '50%',
                width: '35px',
                height: '35px',
                cursor: 'pointer',
                fontSize: '0.9rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.3s ease',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = '#e6c200';
                e.currentTarget.style.transform = 'scale(1.1)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = '#fed700';
                e.currentTarget.style.transform = 'scale(1)';
              }}
              title="Add to Cart"
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
