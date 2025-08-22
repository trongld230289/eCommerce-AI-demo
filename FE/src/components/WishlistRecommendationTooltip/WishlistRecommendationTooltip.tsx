import React, { useState, useRef, useCallback, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faLightbulb, faStar, faSpinner } from '@fortawesome/free-solid-svg-icons';
import { WishlistRecommendation } from '../../services/wishlistRecommendationsService';
import './WishlistRecommendationTooltip.css';

interface WishlistRecommendationTooltipProps {
  recommendation?: WishlistRecommendation;
  children: React.ReactNode;
  isLoading?: boolean;
}

const WishlistRecommendationTooltip: React.FC<WishlistRecommendationTooltipProps> = ({
  recommendation,
  children,
  isLoading = false
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Cleanup animation frame on unmount
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  const handleMouseEnter = (e: React.MouseEvent) => {
    setIsVisible(true);
    updateTooltipPosition(e);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isVisible) {
      updateTooltipPosition(e);
    }
  };

  const handleMouseLeave = () => {
    setIsVisible(false);
    // Cancel any pending animation frame when leaving
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
  };

  const updateTooltipPosition = useCallback((e: React.MouseEvent) => {
    // Cancel any pending animation frame
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }

    // Use requestAnimationFrame for smooth updates
    animationFrameRef.current = requestAnimationFrame(() => {
      const tooltipWidth = 320;
      const tooltipHeight = 200;
      const offset = 15;
      
      let x = e.clientX + offset;
      let y = e.clientY + offset;
      
      // Chỉ điều chỉnh vị trí nếu thực sự vượt quá viewport một cách mượt mà
      if (x + tooltipWidth > window.innerWidth - 10) {
        x = e.clientX - tooltipWidth - offset;
      }
      
      // Thay vì nhảy lên trên, hãy điều chỉnh nhẹ nhàng hơn
      if (y + tooltipHeight > window.innerHeight - 20) {
        // Chỉ di chuyển lên một chút, không nhảy hoàn toàn lên trên
        y = window.innerHeight - tooltipHeight - 20;
      }
      
      // Đảm bảo tooltip không ra khỏi màn hình
      x = Math.max(10, Math.min(x, window.innerWidth - tooltipWidth - 10));
      y = Math.max(10, Math.min(y, window.innerHeight - tooltipHeight - 10));
      
      setPosition({ x, y });
    });
  }, []);
  const formatPrice = (price: number) => {
    // Display price as USD format but keep VND value (e.g., $599.99 instead of 599,000 VND)
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price);
  };

  const formatRating = (rating?: number) => {
    if (!rating) return 'N/A';
    return rating.toFixed(1);
  };

  const calculateDiscount = (price: number, originalPrice?: number) => {
    if (!originalPrice || originalPrice <= price) return null;
    return Math.round(((originalPrice - price) / originalPrice) * 100);
  };

  const discount = recommendation ? calculateDiscount(
    recommendation.product_suggestion.price, 
    recommendation.product_suggestion.original_price
  ) : null;

  return (
    <div 
      className="wishlist-recommendation-container"
      ref={containerRef}
    >
      {children}
      {/* Always show the icon when loading or when there's a recommendation */}
      {(isLoading || recommendation) && (
        <div 
          className={`wishlist-recommendation-icon ${isLoading ? 'loading' : ''}`}
          onMouseEnter={handleMouseEnter}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
        >
          {isLoading ? (
            <FontAwesomeIcon icon={faSpinner} spin />
          ) : (
            <FontAwesomeIcon icon={faLightbulb} />
          )}
        </div>
      )}
      
      {/* Show tooltip when hovering and there's something to display */}
      {isVisible && (isLoading || recommendation) && (
        <div 
          className="wishlist-recommendation-tooltip wishlist-recommendation-tooltip-positioned"
          style={{
            '--tooltip-x': `${position.x}px`,
            '--tooltip-y': `${position.y}px`
          } as React.CSSProperties}
        >
          {isLoading ? (
            <div className="loading-content">
              <FontAwesomeIcon icon={faSpinner} spin className="loading-spinner" />
              <p>Loading recommendation...</p>
            </div>
          ) : recommendation ? (
            <>
              <div className="recommendation-header">
                <FontAwesomeIcon icon={faLightbulb} className="icon" />
                <span className="title">Upgrade Suggestion</span>
              </div>
              
              <div className="recommendation-content">
                <p className="suggestion-text">{recommendation.suggestion}</p>
                
                <div className="product-suggestion">
                  <div className="product-image">
                    <img 
                      src={recommendation.product_suggestion.imageUrl} 
                      alt={recommendation.product_suggestion.name}
                      onError={(e) => {
                        e.currentTarget.src = '/images/placeholder.jpg';
                      }}
                    />
                  </div>
                  
                  <div className="product-info">
                    <h4 className="product-name">{recommendation.product_suggestion.name}</h4>
                    <p className="product-category">{recommendation.product_suggestion.category}</p>
                    
                    <div className="price-section">
                      <div className="current-price">
                        {formatPrice(recommendation.product_suggestion.price)}
                      </div>
                      
                      {recommendation.product_suggestion.original_price && (
                        <div className="original-price">
                          {formatPrice(recommendation.product_suggestion.original_price)}
                        </div>
                      )}
                      
                      {discount && (
                        <div className="discount-badge">
                          -{discount}%
                        </div>
                      )}
                    </div>
                    
                    <div className="product-meta">
                      {recommendation.product_suggestion.rating && (
                        <div className="rating">
                          <FontAwesomeIcon icon={faStar} className="star-icon" />
                          <span>{formatRating(recommendation.product_suggestion.rating)}</span>
                        </div>
                      )}
                    </div>
                    
                    {recommendation.product_suggestion.description && (
                      <p className="product-description">
                        {recommendation.product_suggestion.description}
                      </p>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="recommendation-footer">
                <small>Based on shared wishlists</small>
              </div>
            </>
          ) : (
            <div className="no-recommendation">
              <p>No recommendations available</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default WishlistRecommendationTooltip;
