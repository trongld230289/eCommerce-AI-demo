import React from 'react';
import { useShop } from '../../contexts/ShopContext';
import { Link } from 'react-router-dom';
import './Cart.css';

const Cart = () => {
  const { state, updateQuantity, removeFromCart, getCartTotal, clearCart } = useShop();
  const cart = state.cart;

  if (cart.length === 0) {
    return (
      <div className="cart-empty-container">
        <h2 className="cart-empty-title">
          Your Cart is Empty
        </h2>
        <p className="cart-empty-text">
          Add some products to get started!
        </p>
        <Link
          to="/products"
          className="cart-button-primary"
        >
          Continue Shopping
        </Link>
      </div>
    );
  }

  return (
    <div className="cart-container">
      <h1 className="cart-title">
        Shopping Cart
      </h1>

      <div className="cart-layout">
        {/* Cart Items */}
        <div>
          {cart.map((item) => (
            <div
              key={item.id}
              className="cart-item"
            >
              <img
                src={item.image}
                alt={item.name}
                className="cart-item-image"
              />
              
              <div className="cart-item-info">
                <h3 className="cart-item-name">
                  {item.name}
                </h3>
                <p className="cart-item-category">
                  {item.category}
                </p>
                <div className="cart-item-price">
                  ${item.price}
                </div>
              </div>

              <div className="cart-item-controls">
                <div className="cart-quantity-controls">
                  <button
                    onClick={() => updateQuantity(item.id, item.quantity - 1)}
                    className="cart-quantity-button"
                  >
                    -
                  </button>
                  <span className="cart-quantity-display">
                    {item.quantity}
                  </span>
                  <button
                    onClick={() => updateQuantity(item.id, item.quantity + 1)}
                    className="cart-quantity-button"
                  >
                    +
                  </button>
                </div>

                <button
                  onClick={() => removeFromCart(item.id)}
                  className="cart-remove-button"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}

          <button
            onClick={clearCart}
            className="cart-clear-button"
          >
            Clear Cart
          </button>
        </div>

        {/* Order Summary */}
        <div className="cart-summary">
          <h3 className="cart-summary-title">
            Order Summary
          </h3>

          <div className="cart-summary-subtotal">
            <span>Subtotal:</span>
            <span className="cart-summary-subtotal-amount">${getCartTotal().toFixed(2)}</span>
          </div>

          <div className="cart-summary-row">
            <span>Shipping:</span>
            <span className="cart-summary-shipping">Free</span>
          </div>

          <div className="cart-summary-total">
            <span>Total:</span>
            <span className="cart-summary-total-amount">${getCartTotal().toFixed(2)}</span>
          </div>

          <button className="cart-checkout-button">
            Proceed to Checkout
          </button>

          <Link
            to="/products"
            className="cart-continue-shopping"
          >
            Continue Shopping
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Cart;
