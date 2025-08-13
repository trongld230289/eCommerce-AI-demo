import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTrash, faShoppingCart, faHeart, faPlus, faShare } from '@fortawesome/free-solid-svg-icons';
import { toast } from 'react-toastify';
import { wishlistService } from '../../services/wishlistService';
import { useAuth } from '../../contexts/AuthContext';
import './Wishlist.css';

const Wishlist = () => {
  const [wishlists, setWishlists] = useState([]);
  const [currentWishlist, setCurrentWishlist] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newWishlistName, setNewWishlistName] = useState('');
  const { currentUser } = useAuth();

  const loadWishlists = useCallback(async (preserveCurrentId = null) => {
    if (!currentUser) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const wishlistsData = await wishlistService.getUserWishlists(currentUser.uid);
      setWishlists(wishlistsData);
      
      // Set current wishlist (maintain current selection or use first)
      const currentId = preserveCurrentId;
      if (currentId) {
        const updatedCurrent = wishlistsData.find(w => w.id === currentId);
        setCurrentWishlist(updatedCurrent || (wishlistsData.length > 0 ? wishlistsData[0] : null));
      } else if (wishlistsData.length > 0) {
        setCurrentWishlist(wishlistsData[0]);
      }
    } catch (error) {
      console.error('Error loading wishlists:', error);
      toast.error('Failed to load wishlists');
    } finally {
      setLoading(false);
    }
  }, [currentUser]); // Include currentUser as dependency

  useEffect(() => {
    // Initial load
    loadWishlists();
    
    // Listen for wishlist updates from other components
    const handleWishlistUpdate = () => {
      console.log('Wishlist updated event received');
      // Preserve current selection when reloading
      const currentId = currentWishlist?.id;
      loadWishlists(currentId);
    };
    
    window.addEventListener('wishlistUpdated', handleWishlistUpdate);
    
    return () => {
      window.removeEventListener('wishlistUpdated', handleWishlistUpdate);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty dependency array to run only once - we handle updates via event listeners

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

  const deleteWishlist = async (wishlistId) => {
    if (!currentUser) {
      toast.error('Please login to delete wishlists');
      return;
    }

    if (wishlists.length <= 1) {
      toast.error('Cannot delete the last remaining wishlist');
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

  const shareWishlist = () => {
    if (!currentWishlist) return;
    
    const shareText = `Check out my "${currentWishlist.name}" wishlist with ${wishlistItems.length} items!`;
    const shareUrl = window.location.href;
    
    if (navigator.share) {
      // Use native share API if available
      navigator.share({
        title: `My Wishlist: ${currentWishlist.name}`,
        text: shareText,
        url: shareUrl
      }).catch(err => console.log('Error sharing:', err));
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(`${shareText} ${shareUrl}`).then(() => {
        toast.success('Wishlist link copied to clipboard!');
      }).catch(() => {
        toast.error('Could not copy to clipboard');
      });
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
            <Link to="/login" className="auth-login-btn">
              Login Now
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Get products for current wishlist
  const currentProducts = currentWishlist?.products || [];
  const wishlistItems = currentProducts.map(item => {
    // Backend now returns enhanced product data with full product details
    if (item.product) {
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
            {wishlists.length > 1 && wishlist.name !== 'My Wishlist' && wishlist.name !== 'Favorites' && (
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
                <button className="share-wishlist-btn" onClick={shareWishlist}>
                  <FontAwesomeIcon icon={faShare} /> Share
                </button>
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
                {wishlistItems.map((item) => (
                  <div key={item.id} className="wishlist-item">
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
                        ${item.product?.price?.toFixed(2)}
                      </p>
                      
                      <p className="item-description">
                        {item.product?.description?.substring(0, 100)}
                        {item.product?.description?.length > 100 && '...'}
                      </p>
                      
                      <div className="item-footer">
                        <span className="saved-date">
                          Product ID: #{item.product_id}
                        </span>
                        
                        <div className="item-buttons">
                          <button 
                            className="add-to-cart-btn"
                            onClick={() => {
                              // Add to cart logic here
                              toast.success(`🛒 "${item.product?.name}" added to cart!`, {
                                position: "top-right",
                                autoClose: 3000,
                                hideProgressBar: false,
                                closeOnClick: true,
                                pauseOnHover: true,
                                draggable: true,
                              });
                            }}
                          >
                            <FontAwesomeIcon icon={faShoppingCart} /> Add to Cart
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Wishlist;
