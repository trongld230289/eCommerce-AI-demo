import React, { useState } from 'react';
import ReactDOM from 'react-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHeart } from '@fortawesome/free-solid-svg-icons';
import { toast } from 'react-toastify';
import WishlistModal from '../WishlistModal/WishlistModal';

interface WishlistButtonProps {
  productId: number;
  className?: string;
  onWishlistChange?: (inWishlist: boolean) => void;
}

const WishlistButton: React.FC<WishlistButtonProps> = ({ 
  productId, 
  className = '', 
  onWishlistChange 
}) => {
  const [showModal, setShowModal] = useState(false);
  const [isInWishlist, setIsInWishlist] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('Wishlist button clicked for product:', productId);
    
    const token = localStorage.getItem('token');
    if (!token) {
      console.log('No token found, setting fake token for demo');
      localStorage.setItem('token', 'demo-token');
    }
    
    console.log('Setting showModal to true...');
    setShowModal(true);
  };

  const removeFromWishlist = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/wishlist/${productId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setIsInWishlist(false);
        
        // Dispatch event to update navbar count
        window.dispatchEvent(new Event('wishlistUpdated'));
        
        toast.success('Removed from wishlist!', {
          position: "top-right",
          autoClose: 2000,
        });
        onWishlistChange && onWishlistChange(false);
      } else {
        toast.error('Failed to remove from wishlist', {
          position: "top-right",
          autoClose: 3000,
        });
      }
    } catch (error) {
      console.error('Error removing from wishlist:', error);
      toast.error('Failed to remove from wishlist', {
        position: "top-right",
        autoClose: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSuccess = () => {
    console.log('Wishlist success callback triggered');
    setIsInWishlist(true);
    onWishlistChange && onWishlistChange(true);
    
    // Dispatch event to update wishlist count in navbar
    window.dispatchEvent(new Event('wishlistUpdated'));
    
    // Note: Success toast is handled in WishlistModal component
  };

  const handleClose = () => {
    console.log('Closing modal...');
    setShowModal(false);
  };

  // Render modal using portal to document.body
  const modalPortal = showModal ? ReactDOM.createPortal(
    <WishlistModal
      isOpen={showModal}
      onClose={handleClose}
      productId={productId}
      onSuccess={handleSuccess}
    />,
    document.body
  ) : null;

  console.log('WishlistButton render - showModal:', showModal, 'productId:', productId);

  return (
    <>
      <button
        onClick={handleClick}
        style={{
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
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          backgroundColor: isInWishlist ? '#dc3545' : 'rgba(255,255,255,0.9)',
          color: isInWishlist ? 'white' : '#333',
          zIndex: 1
        }}
        title="Add to Wishlist"
      >
        <FontAwesomeIcon icon={faHeart} />
      </button>
      
      {/* Render modal as portal to document.body */}
      {modalPortal}
    </>
  );
};

export default WishlistButton;