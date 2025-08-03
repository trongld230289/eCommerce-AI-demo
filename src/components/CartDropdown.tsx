import React from 'react';
import { useShop } from '../contexts/ShopContext';
import { Link } from 'react-router-dom';
import { CartItem } from '../contexts/ShopContext';

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
    <div style={{
      position: 'absolute',
      top: '100%',
      right: '0',
      backgroundColor: 'white',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
      borderRadius: '8px',
      minWidth: '400px',
      maxWidth: '450px',
      zIndex: 1000,
      border: '1px solid #e9ecef',
      fontFamily: 'Open Sans, Arial, sans-serif'
    }}>
      {/* Header */}
      <div style={{
        padding: '1rem 1.5rem',
        borderBottom: '1px solid #e9ecef',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <h3 style={{
          margin: 0,
          fontSize: '1.1rem',
          fontWeight: '600',
          color: '#2c3e50'
        }}>
          Shopping Cart ({cart.length})
        </h3>
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            fontSize: '1.5rem',
            cursor: 'pointer',
            color: '#6c757d',
            padding: 0,
            lineHeight: 1
          }}
        >
          ×
        </button>
      </div>

      {/* Cart Items */}
      <div style={{
        maxHeight: '300px',
        overflowY: 'auto'
      }}>
        {cart.length === 0 ? (
          <div style={{
            padding: '2rem',
            textAlign: 'center',
            color: '#6c757d'
          }}>
            <p style={{ margin: 0, fontSize: '0.9rem' }}>Your cart is empty</p>
          </div>
        ) : (
          cart.map((item: CartItem) => (
            <div key={item.id} style={{
              padding: '1rem 1.5rem',
              borderBottom: '1px solid #f8f9fa',
              display: 'flex',
              gap: '1rem',
              alignItems: 'center'
            }}>
              {/* Product Image */}
              <img
                src={item.image}
                alt={item.name}
                style={{
                  width: '60px',
                  height: '60px',
                  objectFit: 'cover',
                  borderRadius: '4px',
                  flexShrink: 0
                }}
              />

              {/* Product Details */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <h4 style={{
                  margin: '0 0 0.5rem 0',
                  fontSize: '0.9rem',
                  fontWeight: '500',
                  color: '#2c3e50',
                  lineHeight: '1.3',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}>
                  {item.name}
                </h4>
                
                {/* Quantity and Price */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  gap: '1rem'
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    <span style={{
                      fontSize: '0.8rem',
                      color: '#6c757d'
                    }}>
                      {item.quantity} ×
                    </span>
                    <span style={{
                      fontSize: '0.9rem',
                      fontWeight: '600',
                      color: '#2c3e50'
                    }}>
                      {formatPrice(item.price)}
                    </span>
                  </div>

                  {/* Quantity Controls */}
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    <button
                      onClick={() => updateQuantity(item.id, Math.max(1, item.quantity - 1))}
                      style={{
                        width: '24px',
                        height: '24px',
                        border: '1px solid #e9ecef',
                        backgroundColor: 'white',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '14px',
                        color: '#6c757d'
                      }}
                    >
                      −
                    </button>
                    <span style={{
                      fontSize: '0.9rem',
                      fontWeight: '500',
                      minWidth: '20px',
                      textAlign: 'center'
                    }}>
                      {item.quantity}
                    </span>
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      style={{
                        width: '24px',
                        height: '24px',
                        border: '1px solid #e9ecef',
                        backgroundColor: 'white',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '14px',
                        color: '#6c757d'
                      }}
                    >
                      +
                    </button>
                  </div>
                </div>
              </div>

              {/* Remove Button */}
              <button
                onClick={() => removeFromCart(item.id)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#dc3545',
                  cursor: 'pointer',
                  padding: '0.25rem',
                  fontSize: '1.2rem',
                  lineHeight: 1,
                  flexShrink: 0
                }}
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
        <div style={{
          padding: '1rem 1.5rem',
          borderTop: '1px solid #e9ecef',
          backgroundColor: '#f8f9fa'
        }}>
          {/* Total */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '1rem'
          }}>
            <span style={{
              fontSize: '1rem',
              fontWeight: '600',
              color: '#2c3e50'
            }}>
              Total:
            </span>
            <span style={{
              fontSize: '1.2rem',
              fontWeight: '700',
              color: '#2c3e50'
            }}>
              {formatPrice(getCartTotal())}
            </span>
          </div>

          {/* Action Buttons */}
          <div style={{
            display: 'flex',
            gap: '0.5rem'
          }}>
            <Link
              to="/cart"
              onClick={onClose}
              style={{
                flex: 1,
                padding: '0.75rem 1rem',
                backgroundColor: 'white',
                color: '#2c3e50',
                border: '1px solid #e9ecef',
                borderRadius: '4px',
                textDecoration: 'none',
                textAlign: 'center',
                fontSize: '0.9rem',
                fontWeight: '500',
                transition: 'all 0.3s ease'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = '#f8f9fa';
                e.currentTarget.style.borderColor = '#d0d7de';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = 'white';
                e.currentTarget.style.borderColor = '#e9ecef';
              }}
            >
              View Cart
            </Link>
            <button
              onClick={onClose}
              style={{
                flex: 1,
                padding: '0.75rem 1rem',
                backgroundColor: '#fed700',
                color: '#333333',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.9rem',
                fontWeight: '600',
                transition: 'all 0.3s ease'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = '#ffc107';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = '#fed700';
              }}
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
