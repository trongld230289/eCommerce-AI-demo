import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHeart, faShoppingCart } from '@fortawesome/free-solid-svg-icons';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ShopProvider, useShop } from './contexts/ShopContext';
import { ToastProvider } from './contexts/ToastContext';
import Cart from './pages/Cart';
import Wishlist from './pages/Wishlist/Wishlist';
import Products from './pages/Products';
import ProductDetails from './pages/ProductDetails';
import Settings from './pages/Settings';
import Home from './pages/Home';
import SearchBar from './components/SearchBar';
import CartDropdown from './components/CartDropdown';
// import MockAuthDialog from './components/MockAuthDialog';
import { useAuthDialog } from './hooks/useAuthDialog';
import Chatbot from './components/Chatbot';
import ChatbotIcon from './components/Chatbot/ChatbotIcon';
import AuthDialog from './components/AuthDialog';

// Add interface for Wishlist type
interface Wishlist {
  id: number;
  name: string;
  item_count?: number;
  products?: number[];
}

// Navigation Component
const Navbar = () => {
  const { currentUser, logout } = useAuth();
  const { state, getCartItemsCount, getCartTotal } = useShop();
  const [isCartDropdownOpen, setIsCartDropdownOpen] = useState(false);
  const [wishlistCount, setWishlistCount] = useState(0);
  const authDialog = useAuthDialog();

  // Load wishlist count from localStorage
  const updateWishlistCount = () => {
    try {
      const savedWishlists = localStorage.getItem('wishlists');
      if (savedWishlists) {
        const wishlists: Wishlist[] = JSON.parse(savedWishlists);
        const totalItems = wishlists.reduce((total: number, wishlist: Wishlist) => {
          return total + (wishlist.products ? wishlist.products.length : 0);
        }, 0);
        setWishlistCount(totalItems);
      } else {
        setWishlistCount(0);
      }
    } catch (error) {
      console.error('Error reading wishlist from localStorage:', error);
      setWishlistCount(0);
    }
  };

  // Update wishlist count on component mount and when storage changes
  React.useEffect(() => {
    updateWishlistCount();
    
    const handleStorageChange = () => {
      updateWishlistCount();
    };
    
    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('wishlistUpdated', handleStorageChange);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('wishlistUpdated', handleStorageChange);
    };
  }, []);
  
  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(price);
  };

  return (
    <>
      {/* Top Header */}
      <div style={{
        backgroundColor: '#f8f9fa',
        borderBottom: '1px solid #e9ecef',
        fontSize: '0.85rem',
        color: '#6c757d',
        fontFamily: 'Open Sans, Arial, sans-serif'
      }}>
        <div style={{
          maxWidth: '1430px',
          margin: '0 auto',
          padding: '0.5rem 1rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span>Welcome to Worldwide Electronics Store</span>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <span>📍 Store Locator</span>
            <span>📦 Track Your Order</span>
            <span>$ Dollar (US)</span>
            {currentUser ? (
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <span>Welcome, {currentUser.displayName || currentUser.email}</span>
                <Link 
                  to="/settings"
                  style={{
                    color: '#0066cc',
                    textDecoration: 'none',
                    fontSize: '0.85rem',
                    fontFamily: 'Open Sans, Arial, sans-serif'
                  }}
                >
                  Settings
                </Link>
                <button
                  onClick={handleLogout}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#0066cc',
                    cursor: 'pointer',
                    fontSize: '0.85rem',
                    fontFamily: 'Open Sans, Arial, sans-serif'
                  }}
                >
                  Sign out
                </button>
              </div>
            ) : (
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <button
                  onClick={() => authDialog.openRegister()}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#6c757d',
                    textDecoration: 'none',
                    fontFamily: 'Open Sans, Arial, sans-serif',
                    cursor: 'pointer',
                    fontSize: '0.85rem'
                  }}
                >
                  Register
                </button>
                <span>or</span>
                <button
                  onClick={() => authDialog.openLogin()}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#6c757d',
                    textDecoration: 'none',
                    fontFamily: 'Open Sans, Arial, sans-serif',
                    cursor: 'pointer',
                    fontSize: '0.85rem'
                  }}
                >
                  Sign in
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Header */}
      <header style={{
        backgroundColor: 'white',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        position: 'sticky',
        top: 0,
        zIndex: 1000
      }}>
        <div style={{
          maxWidth: '1430px',
          margin: '0 auto',
          padding: '1rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: '2rem'
        }}>
          {/* Logo */}
          <Link to="/" style={{
            fontSize: '2.2rem',
            fontWeight: '700',
            color: '#2c3e50',
            textDecoration: 'none',
            letterSpacing: '1px',
            fontFamily: 'Open Sans, Arial, sans-serif'
          }}>
            electro.
          </Link>

          {/* Enhanced Search Bar */}
          <div style={{
            flex: '1',
            maxWidth: '900px',
            position: 'relative'
          }}>
            <SearchBar
              placeholder="Search for Products"
              onSearch={(query, category) => {
                console.log('Search:', query, 'Category:', category);
                // Here you would typically navigate to search results
                // or update the current page with search results
              }}
              onProductSelect={(product) => {
                console.log('Selected product:', product);
                // Here you would typically navigate to product detail page
              }}
            />
          </div>

          {/* Right Actions */}
          <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
            <Link to="/wishlist" style={{ textAlign: 'center', textDecoration: 'none', color: '#2c3e50', position: 'relative' }}>
              <div style={{ fontSize: '1.2rem', position: 'relative' }}>
                <FontAwesomeIcon icon={faHeart} />
                {wishlistCount > 0 && (
                  <span style={{
                    position: 'absolute',
                    top: '-5px',
                    right: '-0px',
                    backgroundColor: '#dc3545',
                    color: 'white',
                    borderRadius: '50%',
                    width: '18px',
                    height: '18px',
                    fontSize: '0.7rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontFamily: 'Open Sans, Arial, sans-serif'
                  }}>
                    {wishlistCount}
                  </span>
                )}
              </div>
              <div style={{ fontSize: '0.8rem', color: '#6c757d', fontFamily: 'Open Sans, Arial, sans-serif' }}>Wishlist</div>
            </Link>
            <div 
              style={{ 
                textAlign: 'center', 
                color: '#2c3e50',
                position: 'relative',
                cursor: 'pointer'
              }}
              onMouseEnter={() => setIsCartDropdownOpen(true)}
              onMouseLeave={() => setIsCartDropdownOpen(false)}
            >
              <div style={{ fontSize: '1.2rem', position: 'relative' }}>
                <FontAwesomeIcon icon={faShoppingCart} />
                {getCartItemsCount() > 0 && (
                  <span style={{
                    position: 'absolute',
                    top: '-5px',
                    right: '7px',
                    backgroundColor: '#dc3545',
                    color: 'white',
                    borderRadius: '50%',
                    width: '18px',
                    height: '18px',
                    fontSize: '0.7rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontFamily: 'Open Sans, Arial, sans-serif'
                  }}>
                    {getCartItemsCount()}
                  </span>
                )}
              </div>
              <div style={{ fontSize: '0.8rem', color: '#6c757d', fontFamily: 'Open Sans, Arial, sans-serif' }}>
                {formatPrice(getCartTotal())}
              </div>
              <CartDropdown 
                isVisible={isCartDropdownOpen} 
                onClose={() => setIsCartDropdownOpen(false)} 
              />
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Bar */}
      <nav style={{
        backgroundColor: '#2c3e50',
        color: 'white',
        fontFamily: 'Open Sans, Arial, sans-serif'
      }}>
        <div style={{
          maxWidth: '1430px',
          margin: '0 auto',
          display: 'flex',
          alignItems: 'center'
        }}>
          <div style={{
            backgroundColor: '#fed700',
            color: '#333333',
            padding: '0.75rem 1.5rem',
            fontWeight: '600',
            cursor: 'pointer',
            width: '250px',
            fontFamily: 'Open Sans, Arial, sans-serif',
            fontSize: '0.8rem',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            ☰ All Departments
          </div>
          <div style={{
            display: 'flex',
            gap: '1.5rem',
            padding: '0 1.5rem'
          }}>
            <span style={{
              color: '#dc3545',
              padding: '0.75rem 0',
              cursor: 'pointer',
              fontWeight: '500',
              fontSize: '0.8rem',
              fontFamily: 'Open Sans, Arial, sans-serif',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              Super Deals
            </span>
            <span style={{ 
              padding: '0.75rem 0', 
              cursor: 'pointer', 
              fontSize: '0.8rem',
              fontFamily: 'Open Sans, Arial, sans-serif',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>Featured Brands</span>
            <span style={{ 
              padding: '0.75rem 0', 
              cursor: 'pointer', 
              fontSize: '0.8rem',
              fontFamily: 'Open Sans, Arial, sans-serif',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>Trending Styles</span>
            <span style={{ 
              padding: '0.75rem 0', 
              cursor: 'pointer', 
              fontSize: '0.8rem',
              fontFamily: 'Open Sans, Arial, sans-serif',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>Gift Cards</span>
          </div>
          <div style={{ 
            marginLeft: 'auto', 
            padding: '0.75rem 1.5rem', 
            fontSize: '0.8rem',
            fontFamily: 'Open Sans, Arial, sans-serif'
          }}>
            Free Shipping on Orders $50+
          </div>
        </div>
      </nav>
      
      {/* Auth Dialog */}
      <AuthDialog 
        isOpen={authDialog.isOpen} 
        onClose={authDialog.close}
        initialMode={authDialog.mode}
      />
    </>
  );
};

function App() {
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);

  return (
    <AuthProvider>
      <ShopProvider>
        <ToastProvider>
          <Router>
            <div className={`App ${isChatbotOpen ? 'chatbot-open' : ''}`} style={{ 
              fontFamily: 'Open Sans, Arial, sans-serif',
              minHeight: '100vh'
            }}>
              <Navbar />
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/cart" element={<Cart />} />
                <Route path="/wishlist" element={<Wishlist />} />
                <Route path="/products" element={<Products />} />
                <Route path="/product/:id" element={<ProductDetails />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
              
              {/* Chatbot Components */}
              <ChatbotIcon 
                onClick={() => setIsChatbotOpen(true)} 
                isVisible={isChatbotOpen} 
              />
              <Chatbot 
                isVisible={isChatbotOpen} 
                onClose={() => setIsChatbotOpen(false)} 
              />
              
              {/* Toast Container with high z-index */}
              <ToastContainer
                position="top-right"
                autoClose={3000}
                hideProgressBar={false}
                newestOnTop={false}
                closeOnClick
                rtl={false}
                pauseOnFocusLoss
                draggable
                pauseOnHover
                style={{ zIndex: 9999999 }}
                toastStyle={{
                  zIndex: 9999999
                }}
              />
            </div>
          </Router>
        </ToastProvider>
      </ShopProvider>
    </AuthProvider>
  );
}

export default App;
