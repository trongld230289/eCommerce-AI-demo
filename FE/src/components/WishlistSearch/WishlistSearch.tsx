import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faClose, faHeart } from '@fortawesome/free-solid-svg-icons';
import { toast } from 'react-toastify';
import { wishlistService, WishlistSearchResult } from '../../services/wishlistService';
import { useAuth } from '../../contexts/AuthContext';
import './WishlistSearch.css';

interface WishlistSearchProps {
  userWishlists: any[];
  onAddProductToWishlist: (productId: number, targetWishlistId: string) => void;
}

const WishlistSearch: React.FC<WishlistSearchProps> = ({ userWishlists, onAddProductToWishlist }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchEmail, setSearchEmail] = useState('');
  const [searchResults, setSearchResults] = useState<WishlistSearchResult[]>([]);
  const [selectedWishlist, setSelectedWishlist] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const { currentUser } = useAuth();

  const handleSearch = async () => {
    if (!searchEmail.trim()) {
      toast.error('Please enter an email address');
      return;
    }

    setLoading(true);
    try {
      const result = await wishlistService.searchWishlists(searchEmail.trim());
      if (result.success) {
        setSearchResults(result.wishlists);
        if (result.wishlists.length === 0) {
          toast.info(result.message);
        } else {
          toast.success(result.message);
        }
      } else {
        toast.error(result.message);
        setSearchResults([]);
      }
    } catch (error) {
      console.error('Search error:', error);
      toast.error('Failed to search wishlists');
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleViewWishlist = async (wishlistId: string) => {
    setLoading(true);
    try {
      const wishlist = await wishlistService.getSharedWishlist(wishlistId);
      setSelectedWishlist(wishlist);
    } catch (error) {
      console.error('Error fetching wishlist:', error);
      toast.error('Failed to load wishlist');
    } finally {
      setLoading(false);
    }
  };

  const handleAddProduct = async (productId: number) => {
    if (!currentUser) {
      toast.error('Please login to add products to your wishlist');
      return;
    }

    if (userWishlists.length === 0) {
      toast.error('You need to have at least one wishlist');
      return;
    }

    // For simplicity, add to the first wishlist
    const targetWishlist = userWishlists[0];
    
    try {
      await wishlistService.addFromSharedWishlist(
        selectedWishlist.id,
        productId,
        targetWishlist.id,
        currentUser.uid
      );
      
      toast.success(`Product added to "${targetWishlist.name}"!`);
      // Note: Keep modal open by not calling onAddProductToWishlist callback
      // onAddProductToWishlist(productId, targetWishlist.id);
    } catch (error) {
      console.error('Error adding product:', error);
      toast.error('Failed to add product to your wishlist');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleDateString();
  };

  return (
    <>
      <div className="wishlist-search-container">
        <div className="search-input-container">
          <input
            type="email"
            placeholder="Enter email to find shared wishlists"
            value={searchEmail}
            onChange={(e) => setSearchEmail(e.target.value)}
            onKeyPress={handleKeyPress}
            className="search-email-input"
          />
          <button 
            onClick={handleSearch}
            disabled={loading}
            className="search-button"
          >
            SEARCH
          </button>
        </div>
      </div>

      {/* Search Results Modal */}
      {(searchResults.length > 0 || selectedWishlist) && (
        <div className="search-modal-overlay" onClick={() => {
          setSearchResults([]);
          setSelectedWishlist(null);
        }}>
          <div className="search-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                {selectedWishlist ? 'Wishlist Details' : `Search Results for "${searchEmail}"`}
              </h3>
              <button 
                className="modal-close-btn"
                onClick={() => {
                  setSearchResults([]);
                  setSelectedWishlist(null);
                }}
              >
                <FontAwesomeIcon icon={faClose} />
              </button>
            </div>

            <div className="modal-content">
              {selectedWishlist ? (
                /* Wishlist Details View */
                <div className="wishlist-details">
                  <div className="wishlist-info">
                    <div className="wishlist-info-left">
                      <h4>
                        {selectedWishlist.name}
                        <span className="item-count">{selectedWishlist.products?.length || 0} items</span>
                      </h4>
                      {selectedWishlist.share_status === 'public' && selectedWishlist.user_name && (
                        <p className="wishlist-owner">by {selectedWishlist.user_name}</p>
                      )}
                      {selectedWishlist.share_status === 'anonymous' && (
                        <p className="wishlist-owner">by Anonymous User</p>
                      )}
                    </div>
                    <button 
                      className="back-btn"
                      onClick={() => setSelectedWishlist(null)}
                    >
                      ← Back to Search Results
                    </button>
                  </div>

                  {selectedWishlist.products && selectedWishlist.products.length > 0 ? (
                    <div className="products-grid">
                      {selectedWishlist.products.map((item: any) => (
                        <div key={item.product_id} className="product-card">
                          <div className="product-image">
                            <img 
                              src={item.product_details?.imageUrl || 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=300&fit=crop&crop=center'} 
                              alt={item.product_details?.name || 'Product'}
                              onError={(e) => {
                                e.currentTarget.src = 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=300&fit=crop&crop=center';
                              }}
                            />
                          </div>
                          <div className="product-info">
                            <h5>{item.product_details?.name || `Product #${item.product_id}`}</h5>
                            <div className="price-section">
                              {item.product_details?.original_price && item.product_details?.original_price !== item.product_details?.price ? (
                                <>
                                  <span className="product-price">${item.product_details?.price?.toFixed(2) || '0.00'}</span>
                                  <span className="original-price">${item.product_details?.original_price?.toFixed(2)}</span>
                                </>
                              ) : (
                                <span className="product-price">${item.product_details?.price?.toFixed(2) || '0.00'}</span>
                              )}
                            </div>
                            <p className="product-description">
                              {item.product_details?.description?.substring(0, 60)}
                              {item.product_details?.description?.length > 60 && '...'}
                            </p>
                            {currentUser && (
                              <button
                                className="add-to-wishlist-btn"
                                onClick={() => handleAddProduct(item.product_id)}
                              >
                                <FontAwesomeIcon icon={faHeart} /> Add to My Wishlist
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-wishlist">
                      <FontAwesomeIcon icon={faHeart} className="empty-icon" />
                      <p>This wishlist is empty</p>
                    </div>
                  )}
                </div>
              ) : (
                /* Search Results List */
                <div className="search-results">
                  {searchResults.map((result) => (
                    <div key={result.id} className="search-result-item">
                      <div className="result-info">
                        <h4>{result.name}</h4>
                        {result.share_status === 'public' && result.user_name && (
                          <p className="result-owner">by {result.user_name} ({result.user_email})</p>
                        )}
                        {result.share_status === 'anonymous' && (
                          <p className="result-owner">by Anonymous User</p>
                        )}
                        <p className="result-details">
                          {result.item_count} items • Created {formatDate(result.created_at)}
                        </p>
                        <span className={`share-badge ${result.share_status}`}>
                          {result.share_status === 'public' ? 'Public' : 'Anonymous'}
                        </span>
                      </div>
                      <button
                        className="view-wishlist-btn"
                        onClick={() => handleViewWishlist(result.id)}
                      >
                        View Wishlist
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default WishlistSearch;
