import React from 'react';
import { Link } from 'react-router-dom';
import { useShop } from '../contexts/ShopContext';
import { useAuth } from '../contexts/AuthContext';
import type { Product } from '../contexts/ShopContext';

const Wishlist: React.FC = () => {
  const { state, addToCart, removeFromWishlist } = useShop();
  const { currentUser } = useAuth();

  const wishlistStyles = {
    container: {
      maxWidth: '1340px',
      margin: '0 auto',
      padding: '2rem',
      backgroundColor: '#f8fafc',
      minHeight: '100vh'
    },
    breadcrumb: {
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      marginBottom: '2rem',
      fontSize: '0.875rem',
      color: '#6b7280'
    },
    breadcrumbLink: {
      color: '#3b82f6',
      textDecoration: 'none'
    },
    header: {
      marginBottom: '2rem'
    },
    title: {
      fontSize: '2rem',
      fontWeight: 'bold',
      color: '#1f2937',
      marginBottom: '0.5rem'
    },
    emptyWishlist: {
      textAlign: 'center' as const,
      padding: '4rem 2rem',
      backgroundColor: 'white',
      borderRadius: '8px',
      border: '1px solid #e5e7eb'
    },
    emptyIcon: {
      fontSize: '4rem',
      marginBottom: '1rem'
    },
    emptyText: {
      fontSize: '1.25rem',
      color: '#6b7280',
      marginBottom: '2rem'
    },
    shopButton: {
      display: 'inline-block',
      backgroundColor: '#3b82f6',
      color: 'white',
      padding: '0.75rem 1.5rem',
      borderRadius: '6px',
      textDecoration: 'none',
      fontSize: '1rem',
      fontWeight: '500',
      transition: 'background-color 0.2s'
    },
    loginPrompt: {
      backgroundColor: '#fef3c7',
      border: '1px solid #f59e0b',
      borderRadius: '8px',
      padding: '2rem',
      textAlign: 'center' as const,
      margin: '2rem 0'
    },
    loginPromptText: {
      color: '#92400e',
      marginBottom: '1rem',
      fontSize: '1.125rem'
    },
    loginLink: {
      color: '#3b82f6',
      textDecoration: 'none',
      fontWeight: '500',
      fontSize: '1rem'
    },
    tableContainer: {
      backgroundColor: 'white',
      borderRadius: '8px',
      border: '1px solid #e5e7eb',
      overflow: 'hidden'
    },
    table: {
      width: '100%',
      borderCollapse: 'collapse' as const
    },
    tableHeader: {
      backgroundColor: '#f9fafb',
      borderBottom: '1px solid #e5e7eb'
    },
    tableHeaderCell: {
      padding: '1rem',
      textAlign: 'left' as const,
      fontSize: '0.875rem',
      fontWeight: '600',
      color: '#374151',
      textTransform: 'uppercase' as const,
      letterSpacing: '0.05em'
    },
    tableRow: {
      borderBottom: '1px solid #f3f4f6',
      transition: 'background-color 0.2s'
    },
    tableCell: {
      padding: '1rem',
      verticalAlign: 'middle' as const
    },
    productCell: {
      display: 'flex',
      alignItems: 'center',
      gap: '1rem'
    },
    productImage: {
      width: '80px',
      height: '80px',
      objectFit: 'cover' as const,
      borderRadius: '6px',
      border: '1px solid #e5e7eb'
    },
    productInfo: {
      flex: 1
    },
    productName: {
      fontSize: '1rem',
      fontWeight: '500',
      color: '#1f2937',
      marginBottom: '0.25rem'
    },
    productBrand: {
      fontSize: '0.875rem',
      color: '#6b7280'
    },
    priceText: {
      fontSize: '1rem',
      fontWeight: '600',
      color: '#1f2937'
    },
    stockStatus: {
      fontSize: '0.875rem',
      fontWeight: '500',
      padding: '0.25rem 0.75rem',
      borderRadius: '4px',
      backgroundColor: '#dcfce7',
      color: '#166534'
    },
    stockStatusOut: {
      backgroundColor: '#fee2e2',
      color: '#dc2626'
    },
    addToCartButton: {
      backgroundColor: '#3b82f6',
      color: 'white',
      border: 'none',
      padding: '0.5rem 1rem',
      borderRadius: '6px',
      fontSize: '0.875rem',
      fontWeight: '500',
      cursor: 'pointer',
      transition: 'background-color 0.2s'
    },
    addToCartButtonDisabled: {
      backgroundColor: '#9ca3af',
      cursor: 'not-allowed'
    },
    removeButton: {
      backgroundColor: 'transparent',
      border: 'none',
      color: '#dc2626',
      cursor: 'pointer',
      fontSize: '1.25rem',
      padding: '0.5rem',
      borderRadius: '4px',
      transition: 'background-color 0.2s'
    }
  };

//   if (!currentUser) {
//     return (
//       <div style={wishlistStyles.container}>
//         <div style={wishlistStyles.breadcrumb}>
//           <Link to="/" style={wishlistStyles.breadcrumbLink}>Home</Link>
//           <span>›</span>
//           <span>Wishlist</span>
//         </div>
        
//         <div style={wishlistStyles.header}>
//           <h1 style={wishlistStyles.title}>My Wishlist</h1>
//         </div>
        
//         <div style={wishlistStyles.loginPrompt}>
//           <p style={wishlistStyles.loginPromptText}>
//             Please log in to view your wishlist
//           </p>
//           <Link to="/login" style={wishlistStyles.loginLink}>
//             Sign in to your account
//           </Link>
//         </div>
//       </div>
//     );
//   }

  if (state.wishlist.length === 0) {
    return (
      <div style={wishlistStyles.container}>
        <div style={wishlistStyles.breadcrumb}>
          <Link to="/" style={wishlistStyles.breadcrumbLink}>Home</Link>
          <span>›</span>
          <span>Wishlist</span>
        </div>
        
        <div style={wishlistStyles.header}>
          <h1 style={wishlistStyles.title}>My wishlist on Electro</h1>
        </div>
        
        <div style={wishlistStyles.emptyWishlist}>
          <div style={wishlistStyles.emptyIcon}>💝</div>
          <p style={wishlistStyles.emptyText}>Your wishlist is empty</p>
          <Link 
            to="/" 
            style={wishlistStyles.shopButton}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#2563eb'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#3b82f6'}
          >
            Start Shopping
          </Link>
        </div>
      </div>
    );
  }

  const handleAddToCart = (product: Product) => {
    addToCart(product);
    // Optional: Show success message or notification
  };

  const handleRemoveFromWishlist = (productId: number) => {
    removeFromWishlist(productId);
  };

  return (
    <div style={wishlistStyles.container}>
      <div style={wishlistStyles.breadcrumb}>
        <Link to="/" style={wishlistStyles.breadcrumbLink}>Home</Link>
        <span>›</span>
        <span>Wishlist</span>
      </div>

      <div style={wishlistStyles.header}>
        <h1 style={wishlistStyles.title}>My wishlist on Electro</h1>
      </div>

      <div style={wishlistStyles.tableContainer}>
        <table style={wishlistStyles.table}>
          <thead style={wishlistStyles.tableHeader}>
            <tr>
              <th style={{...wishlistStyles.tableHeaderCell, width: '4%'}}></th>
              <th style={{...wishlistStyles.tableHeaderCell, width: 'auto'}}>Product</th>
              <th style={{...wishlistStyles.tableHeaderCell, width: '15%'}}>Unit Price</th>
              <th style={{...wishlistStyles.tableHeaderCell, width: '15%'}}>Stock Status</th>
              <th style={{...wishlistStyles.tableHeaderCell, width: '15%'}}></th>
            </tr>
          </thead>
          <tbody>
            {state.wishlist.map((item: Product) => (
              <tr 
                key={item.id} 
                style={wishlistStyles.tableRow}
                onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'}
                onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              >
                <td style={wishlistStyles.tableCell}>
                     <button
                      style={wishlistStyles.removeButton}
                      onClick={() => handleRemoveFromWishlist(item.id)}
                      onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#fee2e2'}
                      onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                      title="Remove from wishlist"
                    >
                      ×
                    </button>
                </td>
                <td style={wishlistStyles.tableCell}>
                  <div style={wishlistStyles.productCell}>
                    <img 
                      src={item.image} 
                      alt={item.name}
                      style={wishlistStyles.productImage}
                    />
                    <div style={wishlistStyles.productInfo}>
                      <h3 style={wishlistStyles.productName}>{item.name}</h3>
                      <p style={wishlistStyles.productBrand}>{item.brand || 'Electronics'}</p>
                    </div>
                  </div>
                </td>
                <td style={wishlistStyles.tableCell}>
                  <span style={wishlistStyles.priceText}>
                    ${item.price.toLocaleString()}
                  </span>
                </td>
                <td style={wishlistStyles.tableCell}>
                  <span style={{
                    ...wishlistStyles.stockStatus,
                    ...(Math.random() > 0.8 ? wishlistStyles.stockStatusOut : {})
                  }}>
                    {Math.random() > 0.8 ? 'Out of stock' : 'In stock'}
                  </span>
                </td>
                <td style={wishlistStyles.tableCell}>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <button
                      style={{
                        ...wishlistStyles.addToCartButton,
                        ...(Math.random() > 0.8 ? wishlistStyles.addToCartButtonDisabled : {})
                      }}
                      onClick={() => handleAddToCart(item)}
                      disabled={Math.random() > 0.8}
                      onMouseOver={(e) => {
                        if (!e.currentTarget.disabled) {
                          e.currentTarget.style.backgroundColor = '#2563eb';
                        }
                      }}
                      onMouseOut={(e) => {
                        if (!e.currentTarget.disabled) {
                          e.currentTarget.style.backgroundColor = '#3b82f6';
                        }
                      }}
                    >
                      Add to Cart
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Wishlist;