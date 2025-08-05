import React from 'react';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faShoppingCart, faEye, faHeart } from '@fortawesome/free-solid-svg-icons';
import { Product } from '../../contexts/ShopContext';
import './SimpleProductCard.css';

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
    <div className="simple-product-card">
      {/* Product Image */}
      <div className="product-image-container">
        <Link to={`/product/${product.id}`} className="product-link">
          <img
            src={product.image}
            alt={product.name}
            className="product-image"
          />
        </Link>
        
        {/* Product Badges */}
        {product.isNew && (
          <span className="product-badge product-badge-new">
            NEW
          </span>
        )}
        
        {product.discount && (
          <span className="product-badge product-badge-discount">
            -${product.discount}
          </span>
        )}

        {/* Hover Overlay with Action Buttons */}
        <div className="product-overlay">
          <Link 
            to={`/product/${product.id}`}
            className="overlay-button"
            title="Quick View"
          >
            <FontAwesomeIcon icon={faEye} />
          </Link>
        </div>
      </div>

      {/* Product Info */}
      <div className="product-info">
        <h3 className="product-title">
          <Link to={`/product/${product.id}`} className="product-title-link">
            {product.name}
          </Link>
        </h3>

        {/* Price and Cart Icon */}
        <div className="price-and-actions">
          <div className="price-container">
            {product.originalPrice && (
              <span className="original-price">
                ${product.originalPrice}
              </span>
            )}
            <span className="current-price">
              ${product.price}
            </span>
          </div>

          {/* Action Buttons Container */}
          <div className="action-buttons">
            {/* Wishlist Button */}
            <button
              onClick={() => onAddToWishlist(product)}
              className={`action-button wishlist-button ${isInWishlist(product.id) ? 'active' : ''}`}
              title="Add to Wishlist"
            >
              <FontAwesomeIcon 
                icon={faHeart} 
                className={`wishlist-icon ${isInWishlist(product.id) ? 'active' : ''}`}
              />
            </button>

            {/* Add to Cart Button */}
            <button
              onClick={() => onAddToCart(product)}
              className="action-button cart-button"
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
