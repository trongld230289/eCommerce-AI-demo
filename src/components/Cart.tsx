import React from 'react';
import { useShop } from './ShopContext';
import { Link } from 'react-router-dom';

const Cart = () => {
  const { cart, updateCartQuantity, removeFromCart, getCartTotal, clearCart } = useShop();

  if (cart.length === 0) {
    return (
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '4rem 1rem',
        textAlign: 'center',
        fontFamily: 'Open Sans, Arial, sans-serif'
      }}>
        <h2 style={{
          fontSize: '2rem',
          marginBottom: '1rem',
          color: '#2c3e50'
        }}>
          Your Cart is Empty
        </h2>
        <p style={{
          fontSize: '1.1rem',
          color: '#6c757d',
          marginBottom: '2rem'
        }}>
          Add some products to get started!
        </p>
        <Link
          to="/products"
          style={{
            backgroundColor: '#fed700',
            color: '#333333',
            padding: '1rem 2rem',
            borderRadius: '4px',
            textDecoration: 'none',
            fontWeight: '600',
            display: 'inline-block'
          }}
        >
          Continue Shopping
        </Link>
      </div>
    );
  }

  return (
    <div style={{
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '2rem 1rem',
      fontFamily: 'Open Sans, Arial, sans-serif'
    }}>
      <h1 style={{
        fontSize: '2.5rem',
        marginBottom: '2rem',
        color: '#2c3e50',
        textAlign: 'center'
      }}>
        Shopping Cart
      </h1>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
        {/* Cart Items */}
        <div>
          {cart.map((item) => (
            <div
              key={item.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1rem',
                padding: '1.5rem',
                backgroundColor: 'white',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                marginBottom: '1rem'
              }}
            >
              <img
                src={item.image}
                alt={item.name}
                style={{
                  width: '80px',
                  height: '80px',
                  objectFit: 'cover',
                  borderRadius: '8px'
                }}
              />
              
              <div style={{ flex: 1 }}>
                <h3 style={{
                  fontSize: '1.1rem',
                  marginBottom: '0.5rem',
                  color: '#2c3e50'
                }}>
                  {item.name}
                </h3>
                <p style={{
                  color: '#6c757d',
                  fontSize: '0.9rem',
                  marginBottom: '0.5rem'
                }}>
                  {item.category}
                </p>
                <div style={{
                  fontSize: '1.2rem',
                  fontWeight: '600',
                  color: '#fed700'
                }}>
                  ${item.price}
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <button
                    onClick={() => updateCartQuantity(item.id, item.quantity - 1)}
                    style={{
                      backgroundColor: '#f8f9fa',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      width: '30px',
                      height: '30px',
                      cursor: 'pointer'
                    }}
                  >
                    -
                  </button>
                  <span style={{
                    minWidth: '30px',
                    textAlign: 'center',
                    fontSize: '1rem',
                    fontWeight: '500'
                  }}>
                    {item.quantity}
                  </span>
                  <button
                    onClick={() => updateCartQuantity(item.id, item.quantity + 1)}
                    style={{
                      backgroundColor: '#f8f9fa',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      width: '30px',
                      height: '30px',
                      cursor: 'pointer'
                    }}
                  >
                    +
                  </button>
                </div>

                <button
                  onClick={() => removeFromCart(item.id)}
                  style={{
                    backgroundColor: '#dc3545',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    padding: '0.5rem 1rem',
                    cursor: 'pointer',
                    fontSize: '0.9rem'
                  }}
                >
                  Remove
                </button>
              </div>
            </div>
          ))}

          <button
            onClick={clearCart}
            style={{
              backgroundColor: '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              padding: '0.75rem 1.5rem',
              cursor: 'pointer',
              fontSize: '1rem',
              marginTop: '1rem'
            }}
          >
            Clear Cart
          </button>
        </div>

        {/* Order Summary */}
        <div style={{
          backgroundColor: 'white',
          padding: '2rem',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          height: 'fit-content'
        }}>
          <h3 style={{
            fontSize: '1.5rem',
            marginBottom: '1.5rem',
            color: '#2c3e50'
          }}>
            Order Summary
          </h3>

          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginBottom: '1rem',
            paddingBottom: '1rem',
            borderBottom: '1px solid #e9ecef'
          }}>
            <span>Subtotal:</span>
            <span style={{ fontWeight: '600' }}>${getCartTotal().toFixed(2)}</span>
          </div>

          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginBottom: '1rem'
          }}>
            <span>Shipping:</span>
            <span style={{ color: '#28a745', fontWeight: '500' }}>Free</span>
          </div>

          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: '1.2rem',
            fontWeight: '600',
            marginBottom: '2rem',
            paddingTop: '1rem',
            borderTop: '2px solid #fed700'
          }}>
            <span>Total:</span>
            <span style={{ color: '#fed700' }}>${getCartTotal().toFixed(2)}</span>
          </div>

          <button style={{
            width: '100%',
            backgroundColor: '#fed700',
            color: '#333333',
            border: 'none',
            borderRadius: '4px',
            padding: '1rem',
            fontSize: '1.1rem',
            fontWeight: '600',
            cursor: 'pointer',
            marginBottom: '1rem'
          }}>
            Proceed to Checkout
          </button>

          <Link
            to="/products"
            style={{
              display: 'block',
              textAlign: 'center',
              color: '#6c757d',
              textDecoration: 'none',
              fontSize: '0.9rem'
            }}
          >
            Continue Shopping
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Cart;
