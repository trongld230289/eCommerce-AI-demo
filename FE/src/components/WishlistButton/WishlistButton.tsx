import React, { useState } from 'react';
import ReactDOM from 'react-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHeart } from '@fortawesome/free-solid-svg-icons';
import { toast } from 'react-toastify';
import WishlistModal from '../WishlistModal/WishlistModal';
import { useAuth } from '../../contexts/AuthContext';

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
  const { currentUser } = useAuth();

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('Wishlist button clicked for product:', productId);
    
    // Check if user is logged in
    if (!currentUser) {
      toast.error('Please login to manage your wishlist', {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
      return;
    }
    
    console.log('Setting showModal to true...');
    setShowModal(true);
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