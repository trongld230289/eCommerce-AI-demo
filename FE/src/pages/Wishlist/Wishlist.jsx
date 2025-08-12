import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTrash, faShoppingCart, faHeart, faPlus, faEdit, faShare } from '@fortawesome/free-solid-svg-icons';
import { toast } from 'react-toastify';
import './Wishlist.css';

// Mock product data - replace with real data from your product context/API
const mockProducts = {
  1: { 
    id: 1, 
    name: 'Wireless Headphones', 
    price: 99.99, 
    imageUrl: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop&crop=center', 
    description: 'High-quality wireless headphones with noise cancellation' 
  },
  2: { 
    id: 2, 
    name: 'Smart Watch', 
    price: 199.99, 
    imageUrl: 'https://images.unsplash.com/photo-1544117519-31a4b719223d?w=300&h=300&fit=crop&crop=center', 
    description: 'Advanced fitness tracking and smart notifications' 
  },
  3: { 
    id: 3, 
    name: 'Bluetooth Speaker', 
    price: 79.99, 
    imageUrl: 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=300&h=300&fit=crop&crop=center', 
    description: 'Portable speaker with excellent sound quality' 
  },
  4: { 
    id: 4, 
    name: 'Gaming Mouse', 
    price: 59.99, 
    imageUrl: 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=300&h=300&fit=crop&crop=center', 
    description: 'Precision gaming mouse with RGB lighting' 
  },
  5: { 
    id: 5, 
    name: 'USB-C Cable', 
    price: 19.99, 
    imageUrl: 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=300&h=300&fit=crop&crop=center', 
    description: 'Fast charging USB-C cable' 
  },
  6: { 
    id: 6, 
    name: 'Laptop Stand', 
    price: 49.99, 
    imageUrl: 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=300&h=300&fit=crop&crop=center', 
    description: 'Adjustable aluminum laptop stand' 
  },
  7: { 
    id: 7, 
    name: 'Wireless Charger', 
    price: 29.99, 
    imageUrl: 'https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=300&h=300&fit=crop&crop=center', 
    description: 'Fast wireless charging pad' 
  },
  8: { 
    id: 8, 
    name: 'Phone Case', 
    price: 24.99, 
    imageUrl: 'https://images.unsplash.com/photo-1601593346740-925612772716?w=300&h=300&fit=crop&crop=center', 
    description: 'Protective phone case with drop protection' 
  }
};

const Wishlist = () => {
  const [wishlists, setWishlists] = useState([]);
  const [currentWishlist, setCurrentWishlist] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newWishlistName, setNewWishlistName] = useState('');

  useEffect(() => {
    loadWishlists();
    
    // Listen for localStorage changes (when items are added from other components)
    const handleStorageChange = () => {
      console.log('Wishlist updated event received'); // Debug log
      loadWishlists();
    };
    
    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('wishlistUpdated', handleStorageChange);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('wishlistUpdated', handleStorageChange);
    };
  }, []);

  const loadWishlists = () => {
    try {
      const savedWishlists = localStorage.getItem('wishlists');
      if (savedWishlists) {
        const wishlistsData = JSON.parse(savedWishlists);
        setWishlists(wishlistsData);
        
        // Set current wishlist (maintain current selection or use first)
        if (currentWishlist) {
          const updatedCurrent = wishlistsData.find(w => w.id === currentWishlist.id);
          setCurrentWishlist(updatedCurrent || wishlistsData[0]);
        } else if (wishlistsData.length > 0) {
          setCurrentWishlist(wishlistsData[0]);
        }
      } else {
        // Create default wishlists if none exist
        const defaultWishlists = [
          { id: 1, name: 'My Favorites ❤️', item_count: 0, products: [] },
          { id: 2, name: 'Gift Ideas 🎁', item_count: 0, products: [] }
        ];
        setWishlists(defaultWishlists);
        setCurrentWishlist(defaultWishlists[0]);
        localStorage.setItem('wishlists', JSON.stringify(defaultWishlists));
      }
    } catch (error) {
      console.error('Error loading wishlists:', error);
      toast.error('Failed to load wishlists');
    } finally {
      setLoading(false);
    }
  };

  // Force refresh when modal closes
  useEffect(() => {
    const handleWishlistUpdate = () => {
      setTimeout(() => {
        loadWishlists();
      }, 100); // Small delay to ensure localStorage is updated
    };
    
    window.addEventListener('wishlistUpdated', handleWishlistUpdate);
    
    return () => {
      window.removeEventListener('wishlistUpdated', handleWishlistUpdate);
    };
  }, [currentWishlist]);

  const createWishlist = () => {
    if (!newWishlistName.trim()) {
      toast.error('Please enter a wishlist name');
      return;
    }

    const newWishlist = {
      id: Date.now(),
      name: newWishlistName.trim(),
      item_count: 0,
      products: []
    };

    const updatedWishlists = [...wishlists, newWishlist];
    setWishlists(updatedWishlists);
    localStorage.setItem('wishlists', JSON.stringify(updatedWishlists));
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
  };

  const removeFromWishlist = (productId) => {
    if (!currentWishlist) return;

    // Find the product being removed for the toast message
    const productBeingRemoved = mockProducts[productId];
    const productName = productBeingRemoved?.name || `Product #${productId}`;

    const updatedWishlists = wishlists.map(wishlist => {
      if (wishlist.id === currentWishlist.id) {
        const updatedProducts = (wishlist.products || []).filter(id => id !== productId);
        return {
          ...wishlist,
          products: updatedProducts,
          item_count: updatedProducts.length
        };
      }
      return wishlist;
    });

    setWishlists(updatedWishlists);
    localStorage.setItem('wishlists', JSON.stringify(updatedWishlists));
    
    // Update current wishlist
    const updatedCurrentWishlist = updatedWishlists.find(w => w.id === currentWishlist.id);
    setCurrentWishlist(updatedCurrentWishlist);
    
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
  };

  const clearWishlist = () => {
    if (!currentWishlist || !window.confirm('Are you sure you want to clear this wishlist?')) {
      return;
    }

    const itemCount = currentWishlist.products?.length || 0;

    const updatedWishlists = wishlists.map(wishlist => {
      if (wishlist.id === currentWishlist.id) {
        return {
          ...wishlist,
          products: [],
          item_count: 0
        };
      }
      return wishlist;
    });

    setWishlists(updatedWishlists);
    localStorage.setItem('wishlists', JSON.stringify(updatedWishlists));
    
    const updatedCurrentWishlist = updatedWishlists.find(w => w.id === currentWishlist.id);
    setCurrentWishlist(updatedCurrentWishlist);
    
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
  };

  const deleteWishlist = (wishlistId) => {
    if (wishlists.length <= 2) {
      toast.error('Cannot delete default wishlists');
      return;
    }

    if (!window.confirm('Are you sure you want to delete this wishlist?')) {
      return;
    }

    // Find the wishlist being deleted for the toast message
    const wishlistToDelete = wishlists.find(w => w.id === wishlistId);
    const wishlistName = wishlistToDelete?.name || 'Wishlist';

    const updatedWishlists = wishlists.filter(w => w.id !== wishlistId);
    setWishlists(updatedWishlists);
    localStorage.setItem('wishlists', JSON.stringify(updatedWishlists));
    
    if (currentWishlist?.id === wishlistId) {
      setCurrentWishlist(updatedWishlists[0]);
    }
    
    // Dispatch event to update navbar count
    window.dispatchEvent(new Event('wishlistUpdated'));
    
    toast.success(`"${wishlistName}" deleted successfully`);
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

  // Get products for current wishlist
  const currentProducts = currentWishlist?.products || [];
  const wishlistItems = currentProducts.map(productId => {
    const product = mockProducts[productId];
    if (!product) {
      return {
        id: `${currentWishlist.id}-${productId}`,
        product_id: productId,
        product: { 
          id: productId, 
          name: `Product #${productId}`, 
          price: 0, 
          imageUrl: 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=300&fit=crop&crop=center',
          description: 'Product not found'
        },
        created_at: new Date().toISOString()
      };
    }
    
    return {
      id: `${currentWishlist.id}-${productId}`,
      product_id: productId,
      product: product,
      created_at: new Date().toISOString()
    };
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
            {/* Only show delete button for custom wishlists (not default ones) */}
            {wishlists.length > 2 && wishlist.id !== 1 && wishlist.id !== 2 && (
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
