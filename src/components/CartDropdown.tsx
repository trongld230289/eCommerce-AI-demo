import React from 'react';
import { useShop } from '../contexts/ShopContext';
import { Link } from 'react-router-dom';
import { CartItem } from '../contexts/ShopContext';
import './CartDropdown.css';

interface CartDropdownProps {
  isVisible: boolean;
  onClose: () => void;
}

const CartDropdown: React.FC<CartDropdownProps> = ({ isVisible, onClose }) => {
  const { state, updateQuantity, removeFromCart, getCartTotal } = useShop();
  const cart = state.cart;

  if (!isVisible) return null;

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(price);
  };

  return (
    <div className="cart-dropdown">
      {/* Header */}
      <div className="cart-dropdown-header">
        <h3 className="cart-dropdown-title">
          Shopping Cart ({cart.length})
        </h3>
        <button
          onClick={onClose}
          className="cart-dropdown-close"
        >
          ×
        </button>
      </div>

      {/* Cart Items */}
      <div className="cart-dropdown-items">
        {cart.length === 0 ? (
          <div className="cart-dropdown-empty">
            <p className="cart-dropdown-empty-text">Your cart is empty</p>
          </div>
        ) : (
          cart.map((item: CartItem) => (
            <div key={item.id} className="cart-dropdown-item">
              {/* Product Image */}
              <img
                src={item.image}
                alt={item.name}
                className="cart-dropdown-item-image"
              />

              {/* Product Details */}
              <div className="cart-dropdown-item-details">
                <h4 className="cart-dropdown-item-name">
                  {item.name}
                </h4>
                
                {/* Quantity and Price */}
                <div className="cart-dropdown-item-row">
                  <div className="cart-dropdown-item-price-info">
                    <span className="cart-dropdown-item-quantity-label">
                      {item.quantity} ×
                    </span>
                    <span className="cart-dropdown-item-price">
                      {formatPrice(item.price)}
                    </span>
                  </div>

                  {/* Quantity Controls */}
                  <div className="cart-dropdown-quantity-controls">
                    <button
                      onClick={() => updateQuantity(item.id, Math.max(1, item.quantity - 1))}
                      className="cart-dropdown-quantity-button"
                    >
                      −
                    </button>
                    <span className="cart-dropdown-quantity-display">
                      {item.quantity}
                    </span>
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      className="cart-dropdown-quantity-button"
                    >
                      +
                    </button>
                  </div>
                </div>
              </div>

              {/* Remove Button */}
              <button
                onClick={() => removeFromCart(item.id)}
                className="cart-dropdown-remove"
                title="Remove item"
              >
                ×
              </button>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      {cart.length > 0 && (
        <div className="cart-dropdown-footer">
          {/* Total */}
          <div className="cart-dropdown-total">
            <span className="cart-dropdown-total-label">
              Total:
            </span>
            <span className="cart-dropdown-total-amount">
              {formatPrice(getCartTotal())}
            </span>
          </div>

          {/* Action Buttons */}
          <div className="cart-dropdown-actions">
            <Link
              to="/cart"
              onClick={onClose}
              className="cart-dropdown-view-cart"
            >
              View Cart
            </Link>
            <button
              onClick={onClose}
              className="cart-dropdown-checkout"
            >
              Checkout
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CartDropdown;
