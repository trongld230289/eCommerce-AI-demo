import React from 'react';
import { useShop } from '../../contexts/ShopContext';
import { useToast } from '../../contexts/ToastContext';
import { Link } from 'react-router-dom';
import SimpleProductCard from '../SimpleProductCard';
import './Wishlist.css';

const Wishlist = () => {
  const { state, removeFromWishlist, addToCart, isInWishlist } = useShop();
  const wishlist = state.wishlist;
  const { showSuccess } = useToast();

  if (wishlist.length === 0) {
    return (
      <div className="wishlist-empty-container">
        <h2 className="wishlist-empty-title">
          Your Wishlist is Empty
        </h2>
        <p className="wishlist-empty-text">
          Save items you love for later!
        </p>
        <Link
          to="/products"
          className="wishlist-button-primary"
        >
          Continue Shopping
        </Link>
      </div>
    );
  }

  const handleAddToCart = (product: any) => {
    addToCart(product);
    showSuccess(`Added to Cart!`, `${product.name} has been added to your cart.`);
  };

  return (
    <div className="wishlist-container">
      <h1 className="wishlist-title">
        My Wishlist
      </h1>

      <div className="wishlist-grid">
        {wishlist.map((product) => (
          <SimpleProductCard
            key={product.id}
            product={product}
            onAddToCart={handleAddToCart}
            onAddToWishlist={() => removeFromWishlist(product.id)}
            isInWishlist={() => true}
          />
        ))}
      </div>

      <div className="wishlist-continue-section">
        <Link
          to="/products"
          className="wishlist-button-secondary"
        >
          Continue Shopping
        </Link>
      </div>
    </div>
  );
};

export default Wishlist;
