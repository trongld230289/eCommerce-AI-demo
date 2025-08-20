import React from 'react';
import { useShop } from '../contexts/ShopContext';
import { useAuth } from '../contexts/AuthContext';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faShoppingCart } from '@fortawesome/free-solid-svg-icons';
import Recommendations from '../components/Recommendations';
import AuthDialog from '../components/AuthDialog';

const Cart = () => {
  const { state, removeFromCart, updateQuantity, clearCart, getCartTotal } = useShop();
  const { currentUser } = useAuth();
  const [couponCode, setCouponCode] = React.useState('');
  const [showAuthDialog, setShowAuthDialog] = React.useState(false);

  const cartStyles = {
    container: {
      maxWidth: '1340px',
      margin: '0 auto',
      padding: '2rem 1rem'
    },
    header: {
      textAlign: 'center' as const,
      marginBottom: '2rem'
    },
    title: {
      fontSize: '2.5rem',
      fontWeight: 'bold',
      color: '#1a202c',
      marginBottom: '0.5rem'
    },
    subtitle: {
      color: '#718096',
      fontSize: '1.1rem'
    },
    emptyCart: {
      textAlign: 'center' as const,
      padding: '4rem 2rem',
      backgroundColor: '#f7fafc',
      borderRadius: '12px',
      margin: '2rem 0'
    },
    emptyIcon: {
      fontSize: '4rem',
      marginBottom: '1rem'
    },
    emptyText: {
      fontSize: '1.25rem',
      color: '#718096',
      marginBottom: '2rem'
    },
    shopButton: {
      backgroundColor: '#2563eb',
      color: 'white',
      padding: '1rem 2rem',
      borderRadius: '8px',
      textDecoration: 'none',
      fontWeight: 'bold',
      display: 'inline-block',
      transition: 'background-color 0.2s'
    },
    cartContent: {
      display: 'grid',
      gridTemplateColumns: '1fr 300px',
      gap: '2rem',
      alignItems: 'start'
    },
    cartItems: {
      backgroundColor: 'white',
      borderRadius: '12px',
      padding: '2rem',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
    },
    cartItem: {
      display: 'flex',
      alignItems: 'center',
      padding: '1.5rem 0',
      borderBottom: '1px solid #e2e8f0'
    },
    itemImage: {
      width: '80px',
      height: '80px',
      objectFit: 'cover' as const,
      borderRadius: '8px',
      marginRight: '1rem'
    },
    itemInfo: {
      flex: 1,
      marginRight: '1rem'
    },
    itemName: {
      fontSize: '1.125rem',
      fontWeight: 'bold',
      marginBottom: '0.5rem',
      color: '#1a202c'
    },
    itemPrice: {
      color: '#dc2626',
      fontSize: '1.125rem',
      fontWeight: 'bold'
    },
    quantityControls: {
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      marginRight: '1rem'
    },
    quantityButton: {
      backgroundColor: '#e2e8f0',
      border: 'none',
      width: '32px',
      height: '32px',
      borderRadius: '4px',
      cursor: 'pointer',
      fontSize: '1.2rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      transition: 'background-color 0.2s'
    },
    quantityDisplay: {
      minWidth: '40px',
      textAlign: 'center' as const,
      fontSize: '1.125rem',
      fontWeight: 'bold'
    },
    removeButton: {
      backgroundColor: '#dc2626',
      color: 'white',
      border: 'none',
      padding: '0.5rem 1rem',
      borderRadius: '6px',
      cursor: 'pointer',
      fontSize: '0.875rem',
      transition: 'background-color 0.2s'
    },
    summary: {
      backgroundColor: 'white',
      borderRadius: '12px',
      padding: '2rem',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
      height: 'fit-content',
      position: 'sticky' as const,
      top: '2rem'
    },
    summaryTitle: {
      fontSize: '1.5rem',
      fontWeight: 'bold',
      marginBottom: '1.5rem',
      color: '#1a202c'
    },
    summaryRow: {
      display: 'flex',
      justifyContent: 'space-between',
      marginBottom: '1rem'
    },
    summaryLabel: {
      color: '#718096'
    },
    summaryValue: {
      fontWeight: 'bold'
    },
    totalRow: {
      display: 'flex',
      justifyContent: 'space-between',
      paddingTop: '1rem',
      borderTop: '2px solid #e2e8f0',
      fontSize: '1.25rem',
      fontWeight: 'bold',
      color: '#1a202c'
    },
    checkoutButton: {
      width: '100%',
      backgroundColor: '#059669',
      color: 'white',
      border: 'none',
      padding: '1rem',
      borderRadius: '8px',
      fontSize: '1.125rem',
      fontWeight: 'bold',
      cursor: 'pointer',
      marginTop: '1.5rem',
      transition: 'background-color 0.2s'
    },
    clearButton: {
      width: '100%',
      backgroundColor: '#dc2626',
      color: 'white',
      border: 'none',
      padding: '0.75rem',
      borderRadius: '8px',
      fontSize: '1rem',
      cursor: 'pointer',
      marginTop: '1rem',
      transition: 'background-color 0.2s'
    },
    loginPrompt: {
      backgroundColor: '#fef3c7',
      border: '1px solid #f59e0b',
      borderRadius: '8px',
      padding: '1rem',
      marginBottom: '1.5rem',
      textAlign: 'center' as const
    },
    loginPromptText: {
      color: '#92400e',
      marginBottom: '0.5rem'
    },
    loginLink: {
      color: '#2563eb',
      textDecoration: 'none',
      fontWeight: 'bold'
    }
  };

  // Check if user is logged in first
  if (!currentUser) {
    return (
      <div style={cartStyles.container}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          marginBottom: '2rem',
          fontSize: '0.875rem',
          color: '#6b7280'
        }}>
          <Link to="/" style={{color: '#3b82f6', textDecoration: 'none'}}>Home</Link>
          <span>›</span>
          <span>Cart</span>
        </div>
        
        <div style={{marginBottom: '2rem'}}>
          <h1 style={{
            fontSize: '2rem',
            fontWeight: 'bold',
            color: '#1f2937',
            marginBottom: '0.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <FontAwesomeIcon icon={faShoppingCart} style={{color: '#3b82f6'}} />
            Shopping Cart
          </h1>
        </div>
        
        <div style={{
          textAlign: 'center' as const,
          padding: '4rem 2rem',
          backgroundColor: '#f7fafc',
          borderRadius: '12px',
          margin: '2rem 0'
        }}>
          <FontAwesomeIcon 
            icon={faShoppingCart} 
            style={{
              fontSize: '4rem',
              marginBottom: '1rem',
              color: '#3b82f6'
            }}
          />
          <h2 style={{
            fontSize: '1.5rem',
            fontWeight: 'bold',
            marginBottom: '0.5rem',
            color: '#1f2937'
          }}>Login Required</h2>
          <p style={{
            fontSize: '1.125rem',
            color: '#718096',
            marginBottom: '2rem'
          }}>Please login to view and manage your shopping cart</p>
          <button 
            onClick={() => setShowAuthDialog(true)}
            style={{
              backgroundColor: '#3b82f6',
              color: 'white',
              padding: '0.75rem 1.5rem',
              borderRadius: '6px',
              border: 'none',
              fontSize: '1rem',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#2563eb'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#3b82f6'}
          >
            Login Now
          </button>
        </div>
        
        <AuthDialog 
          isOpen={showAuthDialog}
          onClose={() => setShowAuthDialog(false)}
          initialMode="login"
        />
      </div>
    );
  }

  if (state.cart.length === 0) {
    return (
      <div style={cartStyles.container}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          marginBottom: '2rem',
          fontSize: '0.875rem',
          color: '#6b7280'
        }}>
          <Link to="/" style={{color: '#3b82f6', textDecoration: 'none'}}>Home</Link>
          <span>›</span>
          <span>Cart</span>
        </div>
        
        <div style={{marginBottom: '2rem'}}>
          <h1 style={{
            fontSize: '2rem',
            fontWeight: 'bold',
            color: '#1f2937',
            marginBottom: '0.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <FontAwesomeIcon icon={faShoppingCart} style={{color: '#3b82f6'}} />
            Shopping Cart
          </h1>
        </div>
        
        <div style={cartStyles.emptyCart}>
          <FontAwesomeIcon 
            icon={faShoppingCart} 
            style={{
              fontSize: '4rem',
              marginBottom: '1rem',
              color: '#3b82f6'
            }}
          />
          <p style={cartStyles.emptyText}>Your cart is empty</p>
          <Link 
            to="/" 
            style={{
              display: 'inline-block',
              backgroundColor: '#3b82f6',
              color: 'white',
              padding: '0.75rem 1.5rem',
              borderRadius: '6px',
              textDecoration: 'none',
              fontSize: '1rem',
              fontWeight: '500',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#2563eb'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#3b82f6'}
          >
            Continue Shopping
          </Link>
        </div>
      </div>
    );
  }

  const handleUpdateQuantity = (id: number, newQuantity: number) => {
    if (newQuantity < 1) {
      removeFromCart(id);
    } else {
      updateQuantity(id, newQuantity);
    }
  };

  const handleClearCart = () => {
    if (window.confirm('Are you sure you want to clear your cart?')) {
      clearCart();
    }
  };

  const handleCouponApply = () => {
    if (couponCode.trim()) {
      alert('Coupon functionality will be implemented soon!');
    }
  };

  return (
    <div style={cartStyles.container}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        marginBottom: '2rem',
        fontSize: '0.875rem',
        color: '#6b7280'
      }}>
        <Link to="/" style={{color: '#3b82f6', textDecoration: 'none'}}>Home</Link>
        <span>›</span>
        <span>Cart</span>
      </div>

      <div style={{marginBottom: '2rem'}}>
        <h1 style={{
          fontSize: '2rem',
          fontWeight: 'bold',
          color: '#1f2937',
          marginBottom: '0.5rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <FontAwesomeIcon icon={faShoppingCart} style={{color: '#3b82f6'}} />
          Shopping Cart
        </h1>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 350px',
        gap: '2rem',
        alignItems: 'start'
      }}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          border: '1px solid #e5e7eb',
          overflow: 'hidden'
        }}>
          <table style={{
            width: '100%',
            borderCollapse: 'collapse' as const
          }}>
            <thead style={{
              backgroundColor: '#f9fafb',
              borderBottom: '1px solid #e5e7eb'
            }}>
              <tr>
                <th style={{
                  padding: '1rem',
                  textAlign: 'left' as const,
                  fontSize: '0.875rem',
                  fontWeight: '600',
                  color: '#374151',
                  textTransform: 'uppercase' as const,
                  letterSpacing: '0.05em',
                  width: '50%'
                }}>Product</th>
                <th style={{
                  padding: '1rem',
                  textAlign: 'left' as const,
                  fontSize: '0.875rem',
                  fontWeight: '600',
                  color: '#374151',
                  textTransform: 'uppercase' as const,
                  letterSpacing: '0.05em',
                  width: '15%'
                }}>Price</th>
                <th style={{
                  padding: '1rem',
                  textAlign: 'left' as const,
                  fontSize: '0.875rem',
                  fontWeight: '600',
                  color: '#374151',
                  textTransform: 'uppercase' as const,
                  letterSpacing: '0.05em',
                  width: '15%'
                }}>Quantity</th>
                <th style={{
                  padding: '1rem',
                  textAlign: 'left' as const,
                  fontSize: '0.875rem',
                  fontWeight: '600',
                  color: '#374151',
                  textTransform: 'uppercase' as const,
                  letterSpacing: '0.05em',
                  width: '15%'
                }}>Total</th>
                <th style={{
                  padding: '1rem',
                  textAlign: 'left' as const,
                  fontSize: '0.875rem',
                  fontWeight: '600',
                  color: '#374151',
                  textTransform: 'uppercase' as const,
                  letterSpacing: '0.05em',
                  width: '5%'
                }}></th>
              </tr>
            </thead>
            <tbody>
              {state.cart.map((item) => (
                <tr 
                  key={item.id} 
                  style={{
                    borderBottom: '1px solid #f3f4f6',
                    transition: 'background-color 0.2s'
                  }}
                  onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                  onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                >
                  <td style={{
                    padding: '1rem',
                    verticalAlign: 'middle' as const
                  }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '1rem'
                    }}>
                      <img 
                        src={item.imageUrl} 
                        alt={item.name}
                        style={{
                          width: '80px',
                          height: '80px',
                          objectFit: 'cover' as const,
                          borderRadius: '6px',
                          border: '1px solid #e5e7eb'
                        }}
                      />
                      <div style={{flex: 1}}>
                        <h3 style={{
                          fontSize: '1rem',
                          fontWeight: '500',
                          color: '#1f2937',
                          marginBottom: '0.25rem'
                        }}>{item.name}</h3>
                        <p style={{
                          fontSize: '0.875rem',
                          color: '#6b7280'
                        }}>{item.category || 'Unknown Category'}</p>
                      </div>
                    </div>
                  </td>
                  <td style={{
                    padding: '1rem',
                    verticalAlign: 'middle' as const
                  }}>
                    <span style={{
                      fontSize: '1rem',
                      fontWeight: '600',
                      color: '#1f2937'
                    }}>
                      ${item.price.toLocaleString()}
                    </span>
                  </td>
                  <td style={{
                    padding: '1rem',
                    verticalAlign: 'middle' as const
                  }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      overflow: 'hidden'
                    }}>
                      <button
                        style={{
                          width: '36px',
                          height: '36px',
                          border: 'none',
                          backgroundColor: '#f9fafb',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '0.875rem',
                          fontWeight: 'bold',
                          color: '#374151',
                          transition: 'background-color 0.2s'
                        }}
                        onClick={() => handleUpdateQuantity(item.id, item.quantity - 1)}
                        onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#e5e7eb'}
                        onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                      >
                        −
                      </button>
                      <input
                        type="text"
                        value={item.quantity}
                        readOnly
                        style={{
                          width: '50px',
                          height: '36px',
                          border: 'none',
                          textAlign: 'center' as const,
                          fontSize: '0.875rem',
                          fontWeight: '500',
                          backgroundColor: 'white'
                        }}
                      />
                      <button
                        style={{
                          width: '36px',
                          height: '36px',
                          border: 'none',
                          backgroundColor: '#f9fafb',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '0.875rem',
                          fontWeight: 'bold',
                          color: '#374151',
                          transition: 'background-color 0.2s'
                        }}
                        onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                        onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#e5e7eb'}
                        onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                      >
                        +
                      </button>
                    </div>
                  </td>
                  <td style={{
                    padding: '1rem',
                    verticalAlign: 'middle' as const
                  }}>
                    <span style={{
                      fontSize: '1rem',
                      fontWeight: '600',
                      color: '#1f2937'
                    }}>
                      ${(item.price * item.quantity).toLocaleString()}
                    </span>
                  </td>
                  <td style={{
                    padding: '1rem',
                    verticalAlign: 'middle' as const
                  }}>
                    <button
                      style={{
                        backgroundColor: 'transparent',
                        border: 'none',
                        color: '#dc2626',
                        cursor: 'pointer',
                        fontSize: '1.25rem',
                        padding: '0.5rem',
                        borderRadius: '4px',
                        transition: 'background-color 0.2s'
                      }}
                      onClick={() => removeFromCart(item.id)}
                      onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#fee2e2'}
                      onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                      title="Remove item"
                    >
                      ×
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '1rem',
            backgroundColor: '#f9fafb',
            borderTop: '1px solid #e5e7eb'
          }}>
            <div style={{
              display: 'flex',
              gap: '0.5rem'
            }}>
              <input
                type="text"
                placeholder="Coupon code"
                value={couponCode}
                onChange={(e) => setCouponCode(e.target.value)}
                style={{
                  padding: '0.5rem 0.75rem',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '0.875rem'
                }}
              />
              <button
                style={{
                  backgroundColor: '#374151',
                  color: 'white',
                  border: 'none',
                  padding: '0.5rem 1rem',
                  borderRadius: '6px',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s'
                }}
                onClick={handleCouponApply}
                onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#1f2937'}
                onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#374151'}
              >
                Apply Coupon
              </button>
            </div>
            <button
              style={{
                backgroundColor: '#6b7280',
                color: 'white',
                border: 'none',
                padding: '0.5rem 1rem',
                borderRadius: '6px',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'background-color 0.2s'
              }}
              onClick={() => alert('Cart updated!')}
              onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#4b5563'}
              onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#6b7280'}
            >
              Update Cart
            </button>
          </div>
        </div>

        <div style={{
          backgroundColor: 'white',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          overflow: 'hidden',
          height: 'fit-content'
        }}>
          <div style={{
            backgroundColor: '#f9fafb',
            padding: '1rem',
            borderBottom: '1px solid #e5e7eb'
          }}>
            <h3 style={{
              fontSize: '1.125rem',
              fontWeight: '600',
              color: '#1f2937',
              margin: 0
            }}>Cart Totals</h3>
          </div>
          
          <div style={{padding: '1rem'}}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: '0.75rem'
            }}>
              <span style={{
                color: '#6b7280',
                fontSize: '0.875rem'
              }}>Subtotal:</span>
              <span style={{
                fontWeight: '500',
                color: '#1f2937',
                fontSize: '0.875rem'
              }}>
                ${getCartTotal().toLocaleString()}
              </span>
            </div>
            
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: '0.75rem'
            }}>
              <span style={{
                color: '#6b7280',
                fontSize: '0.875rem'
              }}>Shipping:</span>
              <span style={{
                fontWeight: '500',
                color: '#1f2937',
                fontSize: '0.875rem'
              }}>Free</span>
            </div>
            
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: '0.75rem'
            }}>
              <span style={{
                color: '#6b7280',
                fontSize: '0.875rem'
              }}>Tax:</span>
              <span style={{
                fontWeight: '500',
                color: '#1f2937',
                fontSize: '0.875rem'
              }}>$0</span>
            </div>
            
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              paddingTop: '1rem',
              borderTop: '1px solid #e5e7eb',
              fontSize: '1.125rem',
              fontWeight: '600',
              color: '#1f2937'
            }}>
              <span>Total:</span>
              <span>${getCartTotal().toLocaleString()}</span>
            </div>
            
            <button
              style={{
                width: '100%',
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                padding: '0.75rem 1rem',
                borderRadius: '6px',
                fontSize: '1rem',
                fontWeight: '500',
                cursor: 'pointer',
                marginTop: '1rem',
                transition: 'background-color 0.2s'
              }}
              onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#2563eb'}
              onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#3b82f6'}
              onClick={() => alert('Checkout functionality will be implemented soon!')}
            >
              Proceed to Checkout
            </button>
          </div>
        </div>
      </div>

      {/* Recommendations Section */}
      {state.cart.length > 0 && (
        <div style={{ 
          marginTop: '3rem', 
          padding: '2rem 1rem', 
          backgroundColor: '#f8fafc',
          borderTop: '1px solid #e2e8f0' 
        }}>
          <div style={{ maxWidth: '1340px', margin: '0 auto' }}>
            <Recommendations 
              limit={6} 
              title="You Might Also Like" 
              className=""
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Cart;
