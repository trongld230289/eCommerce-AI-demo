import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faHeart, faTimes } from '@fortawesome/free-solid-svg-icons';
import { toast } from 'react-toastify';
import { wishlistService, Wishlist } from '../../services/wishlistService';
import { useAuth } from '../../contexts/AuthContext';

interface WishlistModalProps {
  isOpen: boolean;
  onClose: () => void;
  productId: number;
  onSuccess?: () => void;
}

const WishlistModal: React.FC<WishlistModalProps> = ({ 
  isOpen, 
  onClose, 
  productId, 
  onSuccess 
}) => {
  const [wishlists, setWishlists] = useState<Wishlist[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newWishlistName, setNewWishlistName] = useState('');
  const [loading, setLoading] = useState(false);
  const { currentUser } = useAuth();

  // Load wishlists from API
  useEffect(() => {
    const loadWishlists = async () => {
      if (!currentUser) {
        toast.error('Please login to manage your wishlist', {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
        });
        onClose();
        return;
      }

      try {
        setLoading(true);
        const wishlistsData = await wishlistService.getUserWishlists(currentUser.uid);
        setWishlists(wishlistsData);
      } catch (error) {
        console.error('Error loading wishlists:', error);
        toast.error('Failed to load wishlists');
      } finally {
        setLoading(false);
      }
    };

    if (isOpen) {
      loadWishlists();
    }
  }, [isOpen, currentUser, onClose]);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  const createWishlist = async () => {
    if (!currentUser) {
      toast.error('Please login to create a wishlist', {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
      return;
    }

    if (!newWishlistName.trim()) {
      toast.error('Please enter a wishlist name', {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
      return;
    }

    try {
      setLoading(true);
      console.log('Creating wishlist:', newWishlistName);

      // Create wishlist via API
      const newWishlist = await wishlistService.createWishlist({
        name: newWishlistName.trim(),
        user_id: currentUser.uid
      });

      // Add product to the new wishlist
      await wishlistService.addProductToWishlist(newWishlist.id, productId, currentUser.uid);

      // Refresh wishlists
      const updatedWishlists = await wishlistService.getUserWishlists(currentUser.uid);
      setWishlists(updatedWishlists);
      
      setNewWishlistName('');
      setShowCreateForm(false);
      
      window.dispatchEvent(new Event('wishlistUpdated'));
      
      // Close modal first, then show toast
      onSuccess && onSuccess();
      onClose();
      
      // Show toast after a small delay to ensure modal is closed
      setTimeout(() => {
        toast.success(`🎉 Created "${newWishlist.name}" and added product!`, {
          position: "top-right",
          autoClose: 4000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
        });
      }, 300);
      
    } catch (error) {
      console.error('Error creating wishlist:', error);
      toast.error('Failed to create wishlist', {
        position: "top-right",
        autoClose: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const addToWishlist = async (wishlistId: string, wishlistName: string) => {
    if (!currentUser) {
      toast.error('Please login to add to wishlist', {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
      return;
    }

    try {
      setLoading(true);
      
      // Check if product is already in this wishlist
      const wishlist = wishlists.find(w => w.id === wishlistId);
      if (wishlist) {
        const isProductInWishlist = wishlist.products.some(item => item.product_id === productId);
        if (isProductInWishlist) {
          toast.warning(`⚠️ Already in "${wishlistName}"`, {
            position: "top-right",
            autoClose: 3000,
            hideProgressBar: false,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
          });
          return;
        }
      }

      // Add product to wishlist via API
      await wishlistService.addProductToWishlist(wishlistId, productId, currentUser.uid);

      // Refresh wishlists
      const updatedWishlists = await wishlistService.getUserWishlists(currentUser.uid);
      setWishlists(updatedWishlists);
      
      window.dispatchEvent(new Event('wishlistUpdated'));
      
      // Close modal first, then show toast
      onSuccess && onSuccess();
      onClose();
      
      // Show toast after a small delay to ensure modal is closed
      setTimeout(() => {
        toast.success(`❤️ Added to "${wishlistName}"!`, {
          position: "top-right",
          autoClose: 3000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
        });
      }, 300);
      
    } catch (error) {
      console.error('Error adding to wishlist:', error);
      toast.error('Failed to add to wishlist', {
        position: "top-right",
        autoClose: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div 
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.6)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 999999,
        padding: '20px',
        boxSizing: 'border-box'
      }}
      onClick={onClose}
    >
      <div 
        style={{
          background: 'white',
          borderRadius: '12px',
          width: '100%',
          maxWidth: '420px',
          maxHeight: 'calc(100vh - 40px)',
          overflow: 'hidden',
          boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
          position: 'relative',
          animation: 'modalSlideIn 0.3s ease-out'
        }}
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '20px 24px',
          borderBottom: '1px solid #eee',
          backgroundColor: '#f8f9fa'
        }}>
          <h3 style={{ margin: 0, color: '#333', fontSize: '18px', fontWeight: 600 }}>
            Save to wishlist
          </h3>
          <button 
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '18px',
              color: '#666',
              cursor: 'pointer',
              padding: '8px',
              borderRadius: '50%',
              width: '36px',
              height: '36px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'background-color 0.2s'
            }}
          >
            <FontAwesomeIcon icon={faTimes} />
          </button>
        </div>

        {/* Content */}
        <div style={{ 
          padding: '20px 24px', 
          maxHeight: 'calc(100vh - 140px)', 
          overflowY: 'auto' 
        }}>
          <div style={{ 
            textAlign: 'center', 
            marginBottom: '20px',
            padding: '12px',
            backgroundColor: '#e3f2fd',
            borderRadius: '8px',
            color: '#1976d2',
            fontSize: '14px',
            fontWeight: 500
          }}>
            Choose a wishlist for Product #{productId}
          </div>

          {/* Wishlists List */}
          <div style={{ marginBottom: '16px' }}>
            {loading ? (
              <div style={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center',
                padding: '40px',
                color: '#666'
              }}>
                Loading wishlists...
              </div>
            ) : (
              wishlists.map((wishlist) => (
              <div
                key={wishlist.id}
                onClick={() => addToWishlist(wishlist.id, wishlist.name)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '16px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  marginBottom: '8px',
                  border: '1px solid #e0e0e0',
                  transition: 'all 0.2s',
                  backgroundColor: '#fff'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.backgroundColor = '#f8f9fa';
                  e.currentTarget.style.borderColor = '#e74c3c';
                  e.currentTarget.style.transform = 'translateX(4px)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.backgroundColor = '#fff';
                  e.currentTarget.style.borderColor = '#e0e0e0';
                  e.currentTarget.style.transform = 'translateX(0)';
                }}
              >
                <FontAwesomeIcon 
                  icon={faHeart} 
                  style={{ color: '#e74c3c', marginRight: '12px', fontSize: '16px' }}
                />
                <span style={{ flex: 1, color: '#333', fontWeight: 500, fontSize: '15px' }}>
                  {wishlist.name}
                </span>
                <span style={{
                  color: '#666',
                  fontSize: '13px',
                  backgroundColor: '#e9ecef',
                  padding: '4px 8px',
                  borderRadius: '12px'
                }}>
                  {wishlist.item_count || 0} items
                </span>
              </div>
            ))
            )}
          </div>

          {/* Create Form or Create Button */}
          {showCreateForm ? (
            <div style={{
              borderTop: '1px solid #eee',
              paddingTop: '16px',
              marginTop: '16px'
            }}>
              <input
                type="text"
                placeholder="Enter wishlist name"
                value={newWishlistName}
                onChange={(e) => setNewWishlistName(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && createWishlist()}
                autoFocus
                maxLength={50}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  fontSize: '14px',
                  marginBottom: '12px',
                  boxSizing: 'border-box',
                  outline: 'none'
                }}
              />
              <div style={{ display: 'flex', gap: '12px' }}>
                <button 
                  onClick={createWishlist}
                  disabled={!newWishlistName.trim()}
                  style={{
                    flex: 1,
                    padding: '12px 20px',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '14px',
                    fontWeight: 500,
                    cursor: newWishlistName.trim() ? 'pointer' : 'not-allowed',
                    backgroundColor: newWishlistName.trim() ? '#007bff' : '#ccc',
                    color: 'white',
                    transition: 'background-color 0.2s'
                  }}
                >
                  Create
                </button>
                <button 
                  onClick={() => {
                    setShowCreateForm(false);
                    setNewWishlistName('');
                  }}
                  style={{
                    flex: 1,
                    padding: '12px 20px',
                    border: '1px solid #ddd',
                    borderRadius: '6px',
                    fontSize: '14px',
                    fontWeight: 500,
                    cursor: 'pointer',
                    backgroundColor: '#f8f9fa',
                    color: '#666',
                    transition: 'all 0.2s'
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setShowCreateForm(true)}
              style={{
                width: '100%',
                padding: '16px 20px',
                backgroundColor: '#f8f9fa',
                border: '2px dashed #007bff',
                borderRadius: '8px',
                color: '#007bff',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 500,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                marginTop: '16px',
                transition: 'all 0.2s'
              }}
            >
              <FontAwesomeIcon icon={faPlus} /> Create new wishlist
            </button>
          )}
        </div>
      </div>

      <style>{`
        @keyframes modalSlideIn {
          from {
            opacity: 0;
            transform: translateY(-50px) scale(0.9);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }
      `}</style>
    </div>
  );
};

export default WishlistModal;
