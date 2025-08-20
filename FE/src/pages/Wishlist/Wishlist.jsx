import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTrash, faShoppingCart, faHeart, faPlus, faShare, faBolt, faGlobe, faEyeSlash } from '@fortawesome/free-solid-svg-icons';
import { toast } from 'react-toastify';
import { wishlistService } from '../../services/wishlistService';
import { wishlistRecommendationsService } from '../../services/wishlistRecommendationsService';
import { cartService } from '../../services/cartService';
import { eventTrackingService } from '../../services/eventTrackingService';
import { useAuth } from '../../contexts/AuthContext';
import { useShop } from '../../contexts/ShopContext';
import AuthDialog from '../../components/AuthDialog';
import WishlistSearch from '../../components/WishlistSearch/WishlistSearch';
import WishlistRecommendationTooltip from '../../components/WishlistRecommendationTooltip/WishlistRecommendationTooltip';
import './Wishlist.css';

const Wishlist = () => {
  const [wishlists, setWishlists] = useState([]);
  const [currentWishlist, setCurrentWishlist] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newWishlistName, setNewWishlistName] = useState('');
  const [showAuthDialog, setShowAuthDialog] = useState(false);
  const [showShareDropdown, setShowShareDropdown] = useState(false);
  const [recommendations, setRecommendations] = useState(new Map()); // Store recommendations by product_id
  const [productLoadingStates, setProductLoadingStates] = useState(new Map()); // Track loading for each product
  const { currentUser } = useAuth();
  const { addToCart } = useShop();

  // Function to handle adding product to cart
  const handleAddToCart = async (wishlistItem) => {
    if (!currentUser) {
      toast.error('Please log in to add items to cart');
      return;
    }

    try {
      // Debug logging
      console.log('Wishlist item structure:', wishlistItem);
      console.log('Product data:', wishlistItem.product);
      
      // Create proper product object for API calls
      const productForCart = {
        id: wishlistItem.product_id,
        name: wishlistItem.product?.name || `Product #${wishlistItem.product_id}`,
        price: wishlistItem.product?.price || 0,
        original_price: wishlistItem.product?.original_price,
        imageUrl: wishlistItem.product?.imageUrl || 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=300&fit=crop&crop=center',
        category: wishlistItem.product?.category || 'General',
        description: wishlistItem.product?.description || '',
        rating: wishlistItem.product?.rating
      };

      console.log('Product for cart:', productForCart);

      // Add to cart via API
      await cartService.addItemToCart(currentUser.uid, wishlistItem.product_id, 1);
      
      // Add to local cart context to refresh cart icon
      addToCart(productForCart);
      
      // Track user event
      await eventTrackingService.trackEvent({
        event_type: 'add_to_cart',
        user_id: currentUser.uid,
        product_id: wishlistItem.product_id.toString(),
        metadata: {
          product_name: productForCart.name,
          product_category: productForCart.category,
          product_price: productForCart.price,
          source: 'wishlist',
          device: navigator.userAgent
        }
      });
      
      // Dispatch event to refresh cart count in header
      window.dispatchEvent(new Event('cartUpdated'));
      
      toast.success(`🛒 "${productForCart.name}" added to cart!`, {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
    } catch (error) {
      console.error('Error adding to cart:', error);
      toast.error('Failed to add item to cart');
    }
  };

  // Function to handle buy now
  const handleBuyNow = async (wishlistItem) => {
    if (!currentUser) {
      toast.error('Please log in to purchase items');
      return;
    }

    try {
      // Debug logging for buy now
      console.log('Buy now - Wishlist item structure:', wishlistItem);
      console.log('Buy now - Wishlist item.product:', wishlistItem.product);
      
      // Create proper product object
      const productForCart = {
        id: wishlistItem.product_id,
        name: wishlistItem.product?.name || `Product #${wishlistItem.product_id}`,
        price: wishlistItem.product?.price || 0,
        original_price: wishlistItem.product?.original_price,
        imageUrl: wishlistItem.product?.imageUrl || 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=300&fit=crop&crop=center',
        category: wishlistItem.product?.category || 'General',
        description: wishlistItem.product?.description || '',
        rating: wishlistItem.product?.rating
      };
      
      console.log('Buy now - Product for cart:', productForCart);

      // Track user event for purchase
      await eventTrackingService.trackEvent({
        event_type: 'purchase',
        user_id: currentUser.uid,
        product_id: wishlistItem.product_id.toString(),
        metadata: {
          product_name: productForCart.name,
          product_category: productForCart.category,
          product_price: productForCart.price,
          quantity: 1,
          source: 'wishlist_buy_now',
          device: navigator.userAgent
        }
      });
      
      // Show success message immediately
      toast.success(`⚡ Successfully purchased "${productForCart.name}"!`, {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
    } catch (error) {
      console.error('Error processing buy now:', error);
      toast.error('Failed to process purchase');
    }
  };

  const loadWishlists = useCallback(async (preserveCurrentId = null) => {
    console.log('loadWishlists called, currentUser:', currentUser?.uid);
    
    if (!currentUser) {
      console.log('No current user, setting loading to false');
      setLoading(false);
      setWishlists([]);
      setCurrentWishlist(null);
      return;
    }

    try {
      setLoading(true);
      console.log('Fetching wishlists for user:', currentUser.uid);
      const wishlistsData = await wishlistService.getUserWishlists(currentUser.uid);
      console.log('Wishlists loaded:', wishlistsData);
      setWishlists(wishlistsData);
      
      // Set current wishlist (maintain current selection or use first)
      const currentId = preserveCurrentId;
      if (currentId) {
        const updatedCurrent = wishlistsData.find(w => w.id === currentId);
        setCurrentWishlist(updatedCurrent || (wishlistsData.length > 0 ? wishlistsData[0] : null));
      } else if (wishlistsData.length > 0) {
        setCurrentWishlist(wishlistsData[0]);
      } else {
        setCurrentWishlist(null);
      }
    } catch (error) {
      console.error('Error loading wishlists:', error);
      toast.error('Failed to load wishlists');
    } finally {
      setLoading(false);
    }
  }, [currentUser]); // Include currentUser as dependency

  useEffect(() => {
    // Load wishlists when user changes (login/logout)
    console.log('useEffect triggered by loadWishlists change');
    loadWishlists();
  }, [loadWishlists]);

  useEffect(() => {
    // Listen for wishlist updates from other components
    const handleWishlistUpdate = () => {
      console.log('Wishlist updated event received');
      // Preserve current selection when reloading
      const currentId = currentWishlist?.id;
      loadWishlists(currentId);
    };
    
    // Click outside handler for share dropdown
    const handleClickOutside = (event) => {
      if (showShareDropdown && !event.target.closest('.share-wishlist-container')) {
        setShowShareDropdown(false);
      }
    };
    
    window.addEventListener('wishlistUpdated', handleWishlistUpdate);
    document.addEventListener('mousedown', handleClickOutside);
    
    return () => {
      window.removeEventListener('wishlistUpdated', handleWishlistUpdate);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [loadWishlists, currentWishlist?.id, showShareDropdown]);

  const createWishlist = async () => {
    if (!currentUser) {
      toast.error('Please login to create a wishlist');
      return;
    }

    if (!newWishlistName.trim()) {
      toast.error('Please enter a wishlist name');
      return;
    }

    try {
      const newWishlist = await wishlistService.createWishlist({
        name: newWishlistName.trim(),
        user_id: currentUser.uid
      });

      // Refresh wishlists and set the new one as current
      setWishlists(prev => [...prev, newWishlist]);
      setCurrentWishlist(newWishlist);
      setNewWishlistName('');
      setShowCreateForm(false);
      
      // Dispatch event to update navbar count
      window.dispatchEvent(new Event('wishlistUpdated'));
      
      toast.success(`✨ Wishlist "${newWishlist.name}" created successfully!`, {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
    } catch (error) {
      console.error('Error creating wishlist:', error);
      toast.error('Failed to create wishlist');
    }
  };

  const removeFromWishlist = async (productId) => {
    if (!currentWishlist || !currentUser) return;

    try {
      // Get product name from the wishlist item for the toast message
      const productItem = currentWishlist.products.find(item => item.product_id === productId);
      const productName = productItem?.product?.name || `Product #${productId}`;

      // Remove product from wishlist via API
      await wishlistService.removeProductFromWishlist(currentWishlist.id, productId, currentUser.uid);
      
      // Update local state immediately for better UX
      const updatedProducts = currentWishlist.products.filter(item => item.product_id !== productId);
      setCurrentWishlist(prev => ({ ...prev, products: updatedProducts }));
      setWishlists(prev => prev.map(wl => 
        wl.id === currentWishlist.id 
          ? { ...wl, products: updatedProducts }
          : wl
      ));
      
      // Dispatch custom event to notify other components
      window.dispatchEvent(new Event('wishlistUpdated'));
      
      toast.success(`🗑️ "${productName}" removed from "${currentWishlist.name}"`, {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
    } catch (error) {
      console.error('Error removing product from wishlist:', error);
      toast.error('Failed to remove product from wishlist');
      // Reload on error
      loadWishlists(currentWishlist?.id);
    }
  };

  const clearWishlist = async () => {
    if (!currentWishlist || !window.confirm('Are you sure you want to clear this wishlist?')) {
      return;
    }

    const itemCount = currentWishlist.products?.length || 0;

    try {
      // Remove all products from wishlist
      for (const item of currentWishlist.products) {
        await wishlistService.removeProductFromWishlist(currentWishlist.id, item.product_id, currentUser.uid);
      }
      
      // Update local state immediately
      const clearedWishlist = { ...currentWishlist, products: [] };
      setCurrentWishlist(clearedWishlist);
      setWishlists(prev => prev.map(wl => 
        wl.id === currentWishlist.id 
          ? clearedWishlist
          : wl
      ));
      
      // Dispatch custom event to notify other components
      window.dispatchEvent(new Event('wishlistUpdated'));
      
      toast.success(`🧹 Cleared ${itemCount} item${itemCount !== 1 ? 's' : ''} from "${currentWishlist.name}"`, {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
    } catch (error) {
      console.error('Error clearing wishlist:', error);
      toast.error('Failed to clear wishlist');
      // Reload on error
      loadWishlists(currentWishlist?.id);
    }
  };

  // Load recommendations for current wishlist
  const loadRecommendations = useCallback(async () => {
    if (!currentUser || !currentWishlist || !currentWishlist.products || currentWishlist.products.length === 0) {
      return;
    }

    try {
      const productIds = currentWishlist.products.map(item => item.product_id);
      console.log('🔍 Loading recommendations for products on page load:', productIds, 'User:', currentUser.uid);
      
      // Clear existing states
      setRecommendations(new Map());
      setProductLoadingStates(new Map());
      
      // Use progressive loading with individual product loading states
      const recommendationMap = await wishlistRecommendationsService.loadRecommendationsWithProgress(
        productIds, 
        currentUser.uid,
        // Callback when product loading state changes
        (productId, loading) => {
          setProductLoadingStates(prev => {
            const newMap = new Map(prev);
            if (loading) {
              newMap.set(productId, true);
            } else {
              newMap.delete(productId);
            }
            return newMap;
          });
        },
        // Callback when individual recommendation is loaded
        (productId, recommendation) => {
          if (recommendation) {
            setRecommendations(prev => {
              const newMap = new Map(prev);
              newMap.set(productId, recommendation);
              return newMap;
            });
          }
        }
      );
      
      console.log('✅ All recommendations loaded:', recommendationMap.size);
    } catch (error) {
      console.error('Error loading recommendations:', error);
      // Don't show error to user - recommendations are optional
    }
  }, [currentUser, currentWishlist]);

  // Load recommendations when wishlist changes
  useEffect(() => {
    loadRecommendations();
  }, [loadRecommendations]);

  const deleteWishlist = async (wishlistId) => {
    if (!currentUser) {
      toast.error('Please login to delete wishlists');
      return;
    }

    if (!window.confirm('Are you sure you want to delete this wishlist?')) {
      return;
    }

    try {
      await wishlistService.deleteWishlist(wishlistId, currentUser.uid);
      
      // Remove from local state
      const updatedWishlists = wishlists.filter(w => w.id !== wishlistId);
      setWishlists(updatedWishlists);
      
      // Update current wishlist if deleted
      if (currentWishlist?.id === wishlistId) {
        setCurrentWishlist(updatedWishlists.length > 0 ? updatedWishlists[0] : null);
      }
      
      // Dispatch event to update navbar count
      window.dispatchEvent(new Event('wishlistUpdated'));
      
      toast.success('Wishlist deleted successfully!', {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
    } catch (error) {
      console.error('Error deleting wishlist:', error);
      toast.error('Failed to delete wishlist');
    }
  };

  const handleShareOption = async (shareType) => {
    if (!currentWishlist || !currentUser) return;
    
    try {
      const result = await wishlistService.updateShareStatus(currentWishlist.id, currentUser.uid, { share_status: shareType });
      
      if (result.success) {
        // Update local wishlist state
        setCurrentWishlist(prev => ({ ...prev, share_status: shareType }));
        setWishlists(prev => prev.map(wl => 
          wl.id === currentWishlist.id 
            ? { ...wl, share_status: shareType }
            : wl
        ));
        
        // Show success toast with share URL if available
        if (result.share_url && shareType !== 'private') {
          // Copy share URL to clipboard
          navigator.clipboard.writeText(result.share_url).then(() => {
            toast.success(`🔗 ${result.message} Link copied to clipboard!`, {
              position: "top-right",
              autoClose: 4000,
              hideProgressBar: false,
              closeOnClick: true,
              pauseOnHover: true,
              draggable: true,
            });
          }).catch(() => {
            toast.success(`✅ ${result.message}`, {
              position: "top-right",
              autoClose: 3000,
            });
          });
        } else {
          toast.success(`🔒 ${result.message}`, {
            position: "top-right",
            autoClose: 3000,
            hideProgressBar: false,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
          });
        }
      }
    } catch (error) {
      console.error('Error updating share status:', error);
      toast.error('Failed to update share settings');
    } finally {
      setShowShareDropdown(false);
    }
  };

  const shareWishlist = () => {
    if (!currentWishlist) return;
    
    // If already shared, make it private
    if (currentWishlist.share_status && currentWishlist.share_status !== 'private') {
      handleShareOption('private');
    } else {
      // Show dropdown to select share type
      setShowShareDropdown(!showShareDropdown);
    }
  };

  if (loading) {
    return (
      <div className="wishlist-loading">
        <div className="loading-spinner"></div>
        <p>Loading your wishlists...</p>
      </div>
    );
  }

  // Check if user is logged in
  if (!currentUser) {
    return (
      <div className="wishlist-container">
        <div className="wishlist-header">
          <h1>
            <FontAwesomeIcon icon={faHeart} className="wishlist-icon" />
            My Wishlists
          </h1>
        </div>
        <div className="auth-required">
          <div className="auth-message">
            <FontAwesomeIcon icon={faHeart} className="auth-icon" />
            <h2>Login Required</h2>
            <p>Please login to view and manage your wishlists</p>
            <button 
              onClick={() => setShowAuthDialog(true)}
              className="auth-login-btn"
            >
              Login Now
            </button>
          </div>
        </div>
        <AuthDialog 
          isOpen={showAuthDialog}
          onClose={() => setShowAuthDialog(false)}
          initialMode="login"
        />
      </div>
    );
  }

  // Get products for current wishlist
  const currentProducts = currentWishlist?.products || [];
  const wishlistItems = currentProducts.map(item => {
    // Backend now returns enhanced product data with full product details
    if (item.product_details) {
      return {
        id: `${currentWishlist.id}-${item.product_id}`,
        product_id: item.product_id,
        product: item.product_details,
        added_at: item.added_at
      };
    } else if (item.product) {
      // Fallback for legacy product data structure
      return {
        id: `${currentWishlist.id}-${item.product_id}`,
        product_id: item.product_id,
        product: item.product,
        added_at: item.added_at
      };
    } else {
      // Fallback for items without full product data
      return {
        id: `${currentWishlist.id}-${item.product_id}`,
        product_id: item.product_id,
        product: { 
          id: item.product_id, 
          name: `Product #${item.product_id}`, 
          price: 0, 
          imageUrl: 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=300&fit=crop&crop=center',
          description: 'Product details loading...'
        },
        added_at: item.added_at
      };
    }
  });

  return (
    <div className="wishlist-container">
      <div className="wishlist-header">
        <h1>
          <FontAwesomeIcon icon={faHeart} className="wishlist-icon" />
          My Wishlists
        </h1>
        <div className="header-search">
          <WishlistSearch 
            userWishlists={wishlists}
            onAddProductToWishlist={(productId, targetWishlistId) => {
              // Refresh wishlists after adding product
              loadWishlists(currentWishlist?.id);
            }}
          />
        </div>
      </div>

      {/* Wishlist Tabs */}
      <div className="wishlists-tabs">
        {wishlists.map((wishlist) => (
          <div key={wishlist.id} className="wishlist-tab-container">
            <button
              className={`wishlist-tab ${currentWishlist?.id === wishlist.id ? 'active' : ''}`}
              onClick={() => setCurrentWishlist(wishlist)}
              data-text={`${wishlist.name} (${(wishlist.products || []).length})`}
            >
              {wishlist.name}
              <span className="item-count">({(wishlist.products || []).length})</span>
            </button>
            {/* Show delete button for custom wishlists (allow deleting user-created wishlists) */}
            {wishlist.name !== 'My Wishlist' && wishlist.name !== 'Favorites' && (
              <button
                className="delete-wishlist-btn"
                onClick={() => deleteWishlist(wishlist.id)}
                title="Delete wishlist"
              >
                <FontAwesomeIcon icon={faTrash} />
              </button>
            )}
          </div>
        ))}
        
        {showCreateForm ? (
          <div className="create-wishlist-inline">
            <input
              type="text"
              placeholder="Wishlist name"
              value={newWishlistName}
              onChange={(e) => setNewWishlistName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && createWishlist()}
              autoFocus
            />
            <button onClick={createWishlist}>Create</button>
            <button onClick={() => setShowCreateForm(false)}>Cancel</button>
          </div>
        ) : (
          <button 
            className="create-wishlist-tab"
            onClick={() => setShowCreateForm(true)}
          >
            <FontAwesomeIcon icon={faPlus} /> New Wishlist
          </button>
        )}
      </div>

      {currentWishlist && (
        <>
          <div className="current-wishlist-header">
            <h2>{currentWishlist.name}</h2>
            {wishlistItems.length > 0 && (
              <div className="wishlist-actions">
                <div className="share-wishlist-container">
                  <button 
                    className={`share-wishlist-btn ${currentWishlist.share_status && currentWishlist.share_status !== 'private' ? 'shared' : ''}`}
                    onClick={shareWishlist}
                  >
                    <FontAwesomeIcon icon={faShare} /> 
                    {currentWishlist.share_status && currentWishlist.share_status !== 'private' ? 'Shared' : 'Share'}
                  </button>
                  
                  {showShareDropdown && (
                    <div className="share-dropdown">
                      <div className="share-option" onClick={() => handleShareOption('public')}>
                        <FontAwesomeIcon icon={faGlobe} />
                        <div>
                          <div className="option-title">Public</div>
                          <div className="option-desc">Anyone can search and find your name when searching wishlists</div>
                        </div>
                      </div>
                      <div className="share-option" onClick={() => handleShareOption('anonymous')}>
                        <FontAwesomeIcon icon={faEyeSlash} />
                        <div>
                          <div className="option-title">Anonymous</div>
                          <div className="option-desc">Anyone can search and find your wishlist but your name stays hidden</div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                <button className="clear-wishlist-btn" onClick={clearWishlist}>
                  <FontAwesomeIcon icon={faTrash} /> Clear All
                </button>
              </div>
            )}
          </div>

          {wishlistItems.length === 0 ? (
            <div className="empty-wishlist">
              <FontAwesomeIcon icon={faHeart} className="empty-icon" />
              <h2>This wishlist is empty</h2>
              <p>Save items you love to find them easily later</p>
              <p className="empty-hint">
                Click the ❤️ icon on any product to add it to this wishlist
              </p>
              <Link to="/" className="browse-products-btn">
                Browse Products
              </Link>
            </div>
          ) : (
            <div className="wishlist-content">
              <div className="wishlist-stats">
                <p>{wishlistItems.length} item{wishlistItems.length !== 1 ? 's' : ''} saved in "{currentWishlist.name}"</p>
              </div>

              <div className="wishlist-grid">
                {wishlistItems.map((item) => {
                  const recommendation = recommendations.get(item.product_id);
                  const isLoadingRecommendation = productLoadingStates.get(item.product_id) || false;
                  const ItemComponent = (
                    <div key={item.id} className={`wishlist-item ${isLoadingRecommendation ? 'loading-recommendation' : ''} ${recommendation ? 'has-recommendation' : ''}`}>
                      <div className="item-image">
                        <img 
                          src={item.product?.imageUrl || 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=300&fit=crop&crop=center'} 
                          alt={item.product?.name}
                          onError={(e) => {
                            e.target.src = 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=300&fit=crop&crop=center';
                          }}
                        />
                        <div className="item-actions">
                          <button
                            className="remove-item-btn"
                            onClick={() => removeFromWishlist(item.product_id)}
                            title="Remove from wishlist"
                          >
                            <FontAwesomeIcon icon={faTrash} />
                          </button>
                        </div>
                      </div>

                      <div className="item-details">
                        <h3 className="item-name">
                          <Link to={`/product/${item.product_id}`}>
                            {item.product?.name}
                          </Link>
                        </h3>
                        
                        <p className="item-price">
                          <span className="current-price">${item.product?.price?.toFixed(2)}</span>
                          {item.product?.original_price && item.product?.original_price > item.product?.price && (
                            <span className="original-price">${item.product?.original_price?.toFixed(2)}</span>
                          )}
                        </p>
                        
                        <p className="item-description">
                          {item.product?.description?.substring(0, 100)}
                          {item.product?.description?.length > 100 && '...'}
                        </p>
                        
                        <div className="item-footer">
                          <div className="item-buttons">
                            <button 
                              className="add-to-cart-btn"
                              onClick={() => handleAddToCart(item)}
                              title="Add to cart"
                            >
                              <FontAwesomeIcon icon={faShoppingCart} /> Add to Cart
                            </button>
                            
                            <button 
                              className="buy-now-btn"
                              onClick={() => handleBuyNow(item)}
                              title="Buy now"
                            >
                              <FontAwesomeIcon icon={faBolt} /> Buy Now
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  );

                  // Wrap with recommendation tooltip if available
                  return recommendation ? (
                    <WishlistRecommendationTooltip 
                      key={item.id} 
                      recommendation={recommendation}
                    >
                      {ItemComponent}
                    </WishlistRecommendationTooltip>
                  ) : ItemComponent;
                })}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Wishlist;
