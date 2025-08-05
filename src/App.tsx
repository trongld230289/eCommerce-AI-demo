import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHeart, faShoppingCart } from '@fortawesome/free-solid-svg-icons';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ShopProvider, useShop } from './contexts/ShopContext';
import { ToastProvider, useToast } from './contexts/ToastContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Cart from './pages/Cart';
import Wishlist from './pages/Wishlist';
import Products from './pages/Products';
import SimpleProductCard from './components/SimpleProductCard';
import SearchBar from './components/SearchBar';
import CartDropdown from './components/CartDropdown';
import LoginDialog from './components/LoginDialog';
import Chatbot from './components/Chatbot';
import ChatbotIcon from './components/ChatbotIcon';

// Navigation Component
const Navbar = () => {
  const { currentUser, logout } = useAuth();
  const { getCartItemsCount, getCartTotal } = useShop();
  const [isCartDropdownOpen, setIsCartDropdownOpen] = useState(false);
  const [isLoginDialogOpen, setIsLoginDialogOpen] = useState(false);
  
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
                <Link to="/register" style={{ color: '#6c757d', textDecoration: 'none', fontFamily: 'Open Sans, Arial, sans-serif' }}>Register</Link>
                <span>or</span>
                <button
                  onClick={() => setIsLoginDialogOpen(true)}
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
            <Link to="/wishlist" style={{ textAlign: 'center', textDecoration: 'none', color: '#2c3e50' }}>
              <div style={{ fontSize: '1.2rem' }}>
                <FontAwesomeIcon icon={faHeart} />
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
                    top: '-8px',
                    right: '-8px',
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
      
      {/* Login Dialog */}
      <LoginDialog 
        isVisible={isLoginDialogOpen} 
        onClose={() => setIsLoginDialogOpen(false)} 
      />
    </>
  );
};

// Home Page Component
const Home = () => {
  const { addToCart, addToWishlist, isInWishlist } = useShop();
  const { showSuccess, showWarning } = useToast();
  
  const products = [
    { 
      id: 1, 
      name: 'Wireless Audio System Multiroom 360 degree Full base audio', 
      price: 685, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img1.jpg', 
      category: 'Speakers', 
      description: 'Wireless Audio System Multiroom 360 degree Full base audio system with premium sound quality', 
      rating: 5, 
      isNew: false, 
      originalPrice: 799, 
      discount: 114,
      brand: 'Audio Tech',
      tags: ['wireless', 'multiroom', 'speaker', 'audio'],
      color: 'Black'
    },
    { 
      id: 2, 
      name: 'Tablet White EliteBook Revolve 810 G2', 
      price: 1999, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg', 
      category: 'Tablets', 
      description: 'Tablet White EliteBook Revolve 810 G2 with touchscreen and premium performance', 
      rating: 5, 
      isNew: false, 
      originalPrice: 2299, 
      discount: 300,
      brand: 'EliteBook',
      tags: ['tablet', 'touchscreen', 'business', 'premium'],
      color: 'White'
    },
    { 
      id: 3, 
      name: 'Purple Solo 2 Wireless', 
      price: 685, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img3.jpg', 
      category: 'Headphones', 
      description: 'Purple Solo 2 Wireless headphones with premium sound and noise cancellation', 
      rating: 4, 
      isNew: false, 
      originalPrice: 799, 
      discount: 114,
      brand: 'Solo',
      tags: ['headphones', 'wireless', 'noise-cancelling', 'premium'],
      color: 'Purple'
    },
    { 
      id: 4, 
      name: 'Smartphone 6S 32GB LTE', 
      price: 685, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img4.jpg', 
      category: 'Smartphones', 
      description: 'Smartphone 6S 32GB LTE with advanced camera and fast processing', 
      rating: 5, 
      isNew: false, 
      originalPrice: 799, 
      discount: 114,
      brand: 'TechPhone',
      tags: ['smartphone', '32gb', 'lte', 'camera'],
      color: 'Space Gray'
    },
    { 
      id: 5, 
      name: 'Widescreen NX Mini F1 SMART NX', 
      price: 685, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img5.jpg', 
      category: 'Cameras', 
      description: 'Widescreen NX Mini F1 SMART NX professional camera with 4K recording', 
      rating: 4, 
      isNew: true, 
      originalPrice: 799, 
      discount: 114,
      brand: 'NX',
      tags: ['camera', 'professional', '4k', 'smart'],
      color: 'Black'
    },
    { 
      id: 6, 
      name: 'Full Color LaserJet Pro M452dn', 
      price: 685, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img6.jpg', 
      category: 'Printers', 
      description: 'Full Color LaserJet Pro M452dn high-quality printer for office use', 
      rating: 5, 
      isNew: false, 
      originalPrice: 799, 
      discount: 114,
      brand: 'LaserJet',
      tags: ['printer', 'color', 'office', 'professional'],
      color: 'White'
    },
    { 
      id: 7, 
      name: 'Game Console Controller + USB 3.0 Cable', 
      price: 79, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img7.jpg', 
      category: 'Gaming', 
      description: 'Wireless game controller with USB 3.0 cable for premium gaming experience', 
      rating: 4, 
      isNew: false, 
      originalPrice: 99, 
      discount: 20,
      brand: 'GameTech',
      tags: ['controller', 'gaming', 'wireless', 'usb'],
      color: 'Black'
    },
    { 
      id: 8, 
      name: 'Camera C430W 4k Waterproof', 
      price: 685, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img8.jpg', 
      category: 'Cameras', 
      description: 'Camera C430W 4k Waterproof action camera for extreme sports', 
      rating: 5, 
      isNew: true, 
      originalPrice: 799, 
      discount: 114,
      brand: 'ActionCam',
      tags: ['camera', '4k', 'waterproof', 'action'],
      color: 'Orange'
    },
    { 
      id: 9, 
      name: 'GameConsole Destiny Special Edition', 
      price: 685, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img9.jpg', 
      category: 'Gaming', 
      description: 'GameConsole Destiny Special Edition with exclusive games and content', 
      rating: 5, 
      isNew: true, 
      originalPrice: 799, 
      discount: 114,
      brand: 'GameConsole',
      tags: ['console', 'gaming', 'special-edition', 'destiny'],
      color: 'White'
    },
    { 
      id: 10, 
      name: 'Tablet Air 3 WiFi 64GB Gold', 
      price: 629, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img10.jpg', 
      category: 'Tablets', 
      description: 'Tablet Air 3 WiFi 64GB Gold with retina display and all-day battery', 
      rating: 5, 
      isNew: false, 
      originalPrice: 749, 
      discount: 120,
      brand: 'TabletAir',
      tags: ['tablet', 'wifi', '64gb', 'retina'],
      color: 'Gold'
    },
    { 
      id: 11, 
      name: 'Pendrive USB 3.0 Flash 64 GB', 
      price: 110, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img11.jpg', 
      category: 'Accessories', 
      description: 'Pendrive USB 3.0 Flash 64 GB high-speed storage device', 
      rating: 4, 
      isNew: false, 
      originalPrice: 130, 
      discount: 20,
      brand: 'FlashDrive',
      tags: ['usb', 'storage', '64gb', 'portable'],
      color: 'Silver'
    },
    { 
      id: 12, 
      name: 'White Solo 2 Wireless', 
      price: 110, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img12.jpg', 
      category: 'Headphones', 
      description: 'White Solo 2 Wireless headphones with crystal clear sound', 
      rating: 4, 
      isNew: false, 
      originalPrice: 140, 
      discount: 30,
      brand: 'Solo',
      tags: ['headphones', 'wireless', 'premium', 'clear-sound'],
      color: 'White'
    },
    { 
      id: 13, 
      name: 'Smartwatch 2.0 LTE Wifi', 
      price: 110, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img13.jpg', 
      category: 'Smartwatches', 
      description: 'Smartwatch 2.0 LTE Wifi with health monitoring and GPS', 
      rating: 5, 
      isNew: true, 
      originalPrice: 150, 
      discount: 40,
      brand: 'SmartTime',
      tags: ['smartwatch', 'lte', 'wifi', 'health'],
      color: 'Black'
    },
    { 
      id: 14, 
      name: 'Gear Virtual Reality', 
      price: 799, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img14.jpg', 
      category: 'VR', 
      description: 'Gear Virtual Reality headset for immersive gaming and entertainment', 
      rating: 5, 
      isNew: true, 
      originalPrice: 899, 
      discount: 100,
      brand: 'VRGear',
      tags: ['vr', 'virtual-reality', 'gaming', 'immersive'],
      color: 'Black'
    },
    { 
      id: 15, 
      name: 'Gaming Laptop Pro 15"', 
      price: 1299, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img15.jpg', 
      category: 'Laptops', 
      description: 'Gaming Laptop Pro 15" with high-performance graphics and fast processor', 
      rating: 5, 
      isNew: true, 
      originalPrice: 1499, 
      discount: 200,
      brand: 'GamerTech',
      tags: ['laptop', 'gaming', 'high-performance', '15-inch'],
      color: 'Black'
    },
    { 
      id: 16, 
      name: 'Bluetooth Speaker Portable', 
      price: 149, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img16.jpg', 
      category: 'Speakers', 
      description: 'Bluetooth Speaker Portable with 360-degree sound and water resistance', 
      rating: 4, 
      isNew: false, 
      originalPrice: 179, 
      discount: 30,
      brand: 'SoundWave',
      tags: ['bluetooth', 'portable', 'waterproof', '360-sound'],
      color: 'Blue'
    },
    { 
      id: 17, 
      name: 'Professional DSLR Camera', 
      price: 2199, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img17.jpg', 
      category: 'Cameras', 
      description: 'Professional DSLR Camera with 24MP sensor and advanced autofocus', 
      rating: 5, 
      isNew: true, 
      originalPrice: 2499, 
      discount: 300,
      brand: 'ProCam',
      tags: ['dslr', 'professional', '24mp', 'autofocus'],
      color: 'Black'
    },
    { 
      id: 18, 
      name: 'Wireless Earbuds Pro', 
      price: 199, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img18.jpg', 
      category: 'Headphones', 
      description: 'Wireless Earbuds Pro with active noise cancellation and long battery life', 
      rating: 5, 
      isNew: true, 
      originalPrice: 249, 
      discount: 50,
      brand: 'AudioPro',
      tags: ['earbuds', 'wireless', 'noise-cancelling', 'long-battery'],
      color: 'White'
    },
    { 
      id: 19, 
      name: 'Smart TV 55" 4K Ultra HD', 
      price: 899, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img19.jpg', 
      category: 'TV', 
      description: 'Smart TV 55" 4K Ultra HD with streaming apps and voice control', 
      rating: 5, 
      isNew: false, 
      originalPrice: 1099, 
      discount: 200,
      brand: 'SmartVision',
      tags: ['smart-tv', '55-inch', '4k', 'streaming'],
      color: 'Black'
    },
    { 
      id: 20, 
      name: 'Mechanical Gaming Keyboard RGB', 
      price: 129, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img20.jpg', 
      category: 'Gaming', 
      description: 'Mechanical Gaming Keyboard RGB with custom switches and backlighting', 
      rating: 4, 
      isNew: false, 
      originalPrice: 159, 
      discount: 30,
      brand: 'GameKeys',
      tags: ['keyboard', 'mechanical', 'rgb', 'gaming'],
      color: 'Black'
    }
  ];

  const categories = [
    { name: 'Smartphones', icon: '📱', count: '3 Items' },
    { name: 'Laptops', icon: '💻', count: '2 Items' },
    { name: 'Headphones', icon: '🎧', count: '3 Items' },
    { name: 'Tablets', icon: '📱', count: '2 Items' },
    { name: 'Smartwatches', icon: '⌚', count: '1 Item' },
    { name: 'Cameras', icon: '📷', count: '3 Items' },
    { name: 'Gaming', icon: '🎮', count: '3 Items' },
    { name: 'Speakers', icon: '🔊', count: '2 Items' },
    { name: 'TV', icon: '📺', count: '1 Item' },
    { name: 'VR', icon: '🥽', count: '1 Item' },
    { name: 'Printers', icon: '�️', count: '1 Item' },
    { name: 'Accessories', icon: '🔌', count: '1 Item' }
  ];

  const handleAddToCart = (product: any) => {
    addToCart(product);
    showSuccess(`Added to Cart!`, `${product.name} has been added to your cart.`);
  };
  
  const handleAddToWishlist = (product: any) => {
    if (isInWishlist(product.id)) {
      showWarning(`Already in Wishlist!`, `${product.name} is already in your wishlist.`);
    } else {
      addToWishlist(product);
      showSuccess(`Added to Wishlist!`, `${product.name} has been added to your wishlist.`);
    }
  };

  const homeStyles = {
    container: {
      backgroundColor: '#ffffff',
      minHeight: '100vh',
      fontFamily: 'Open Sans, Arial, sans-serif'
    },
    
    // Hero Banner Section
    heroBanner: {
       background: 'url("https://transvelo.github.io/electro-html/2.0/assets/img/1920X422/img1.jpg")',
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
      color: '#333333',
      padding: '0',
      marginBottom: '0'
    },
    heroContainer: {
      maxWidth: '1430px',
      margin: '0 auto',
      padding: '0 0rem',
      display: 'flex',
      gap: '0',
      alignItems: 'flex-start'
    },
    heroContent: {
      flex: 1,
      background: '',
      color: 'white',
      padding: '3rem 2rem',
      borderRadius: '0',
      position: 'relative' as const,
      minHeight: '400px',
      display: 'flex',
      flexDirection: 'column' as const,
      justifyContent: 'center'
    },
    heroTitle: {
      fontSize: '3.5rem',
      fontWeight: '700',
      marginBottom: '1rem',
      lineHeight: '1.1',
      letterSpacing: '0.5px',
      fontFamily: 'Open Sans, Arial, sans-serif',
      textTransform: 'uppercase' as const,
      color: '#353E48'
    },
    heroSubtitle: {
      fontSize: '0.8rem',
      marginBottom: '0.5rem',
      opacity: 0.9,
      lineHeight: '1.5',
      fontWeight: '500',
      fontFamily: 'Open Sans, Arial, sans-serif',
      textTransform: 'uppercase' as const,
      letterSpacing: '1.5px',
      color: '#353E48'
    },
    heroPrice: {
      fontSize: '2.5rem',
      fontWeight: '300',
      marginBottom: '2rem',
      color: '#353E48',
      fontFamily: 'Open Sans, Arial, sans-serif'
    },
    heroButton: {
      backgroundColor: '#fed700',
      color: '#333333',
      padding: '0.7rem 1rem',
      borderRadius: '4px',
      textDecoration: 'none',
      fontWeight: '700',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      transition: 'all 0.3s ease',
      border: 'none',
      cursor: 'pointer',
      textTransform: 'uppercase' as const,
      fontFamily: 'Open Sans, Arial, sans-serif',
      fontSize: '0.8rem',
      letterSpacing: '0.3px',
      width: 'auto',
      maxWidth: '130px',
      textAlign: 'center' as const,
      lineHeight: '1',
      minHeight: '35px'
    },
    heroImage: {
      width: '400px',
      height: 'auto',
      objectFit: 'contain' as const,
      position: 'absolute' as const,
      right: '1rem',
      top: '50%',
      transform: 'translateY(-50%)'
    }
  };

  return (
    <div style={homeStyles.container}>
      {/* Hero Banner với Slider */}
      <section style={homeStyles.heroBanner}>
        <div style={homeStyles.heroContainer}>
          {/* Side Navigation */}
          <div style={{
            width: '250px',
            backgroundColor: '#f8f9fa',
            padding: '0',
            borderRadius: '0',
            border: '1px solid #e9ecef'
          }}>
            <div style={{ 
              padding: '0.6rem 1rem', 
              fontWeight: '500', 
              color: '#2c3e50', 
              borderBottom: '1px solid #e9ecef',
              fontFamily: 'Open Sans, Arial, sans-serif',
              fontSize: '0.75rem',
              textAlign: 'left',
              cursor: 'pointer'
            }}>
              Value of the Day
            </div>
            <div style={{ 
              padding: '0.6rem 1rem', 
              fontWeight: '500', 
              color: '#2c3e50', 
              borderBottom: '1px solid #e9ecef',
              fontFamily: 'Open Sans, Arial, sans-serif',
              fontSize: '0.75rem',
              textAlign: 'left',
              cursor: 'pointer'
            }}>
              Top 100 Offers
            </div>
            <div style={{ 
              padding: '0.6rem 1rem', 
              fontWeight: '500', 
              color: '#2c3e50', 
              borderBottom: '1px solid #e9ecef',
              fontFamily: 'Open Sans, Arial, sans-serif',
              fontSize: '0.75rem',
              textAlign: 'left',
              cursor: 'pointer'
            }}>
              New Arrivals
            </div>
            <div style={{ 
              padding: '0.6rem 1rem', 
              fontWeight: '500', 
              color: '#2c3e50', 
              borderBottom: '1px solid #e9ecef',
              fontFamily: 'Open Sans, Arial, sans-serif',
              fontSize: '0.75rem',
              textAlign: 'left',
              cursor: 'pointer',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span>Computers & Accessories</span>
              <span style={{ fontSize: '0.6rem', color: '#6c757d' }}>→</span>
            </div>
            <div style={{ 
              padding: '0.6rem 1rem', 
              fontWeight: '500', 
              color: '#2c3e50', 
              borderBottom: '1px solid #e9ecef',
              fontFamily: 'Open Sans, Arial, sans-serif',
              fontSize: '0.75rem',
              textAlign: 'left',
              cursor: 'pointer',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span>Cameras, Audio & Video</span>
              <span style={{ fontSize: '0.6rem', color: '#6c757d' }}>→</span>
            </div>
            <div style={{ 
              padding: '0.6rem 1rem', 
              fontWeight: '500', 
              color: '#2c3e50', 
              borderBottom: '1px solid #e9ecef',
              fontFamily: 'Open Sans, Arial, sans-serif',
              fontSize: '0.75rem',
              textAlign: 'left',
              cursor: 'pointer',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span>Mobiles & Tablets</span>
              <span style={{ fontSize: '0.6rem', color: '#6c757d' }}>→</span>
            </div>
            <div style={{ 
              padding: '0.6rem 1rem', 
              fontWeight: '500', 
              color: '#2c3e50', 
              borderBottom: '1px solid #e9ecef',
              fontFamily: 'Open Sans, Arial, sans-serif',
              fontSize: '0.75rem',
              textAlign: 'left',
              cursor: 'pointer',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span>Movies, Music & Video Game</span>
              <span style={{ fontSize: '0.6rem', color: '#6c757d' }}>→</span>
            </div>
            <div style={{ 
              padding: '0.6rem 1rem', 
              fontWeight: '500', 
              color: '#2c3e50', 
              borderBottom: '1px solid #e9ecef',
              fontFamily: 'Open Sans, Arial, sans-serif',
              fontSize: '0.75rem',
              textAlign: 'left',
              cursor: 'pointer',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span>TV & Audio</span>
              <span style={{ fontSize: '0.6rem', color: '#6c757d' }}>→</span>
            </div>
            <div style={{ 
              padding: '0.6rem 1rem', 
              fontWeight: '500', 
              color: '#2c3e50', 
              borderBottom: '1px solid #e9ecef',
              fontFamily: 'Open Sans, Arial, sans-serif',
              fontSize: '0.75rem',
              textAlign: 'left',
              cursor: 'pointer',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span>Watches & Eyewear</span>
              <span style={{ fontSize: '0.6rem', color: '#6c757d' }}>→</span>
            </div>
            <div style={{ 
              padding: '0.6rem 1rem', 
              fontWeight: '500', 
              color: '#2c3e50', 
              borderBottom: '1px solid #e9ecef',
              fontFamily: 'Open Sans, Arial, sans-serif',
              fontSize: '0.75rem',
              textAlign: 'left',
              cursor: 'pointer',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span>Car, Motorbike & Industrial</span>
              <span style={{ fontSize: '0.6rem', color: '#6c757d' }}>→</span>
            </div>
            <div style={{ 
              padding: '0.6rem 1rem', 
              fontWeight: '500', 
              color: '#2c3e50',
              fontFamily: 'Open Sans, Arial, sans-serif',
              fontSize: '0.75rem',
              textAlign: 'left',
              cursor: 'pointer',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span>Accessories</span>
              <span style={{ fontSize: '0.6rem', color: '#6c757d' }}>→</span>
            </div>
          </div>
          
          {/* Main Hero Content - Slider */}
          <div style={{ flex: 1, position: 'relative', }}>
            <div style={homeStyles.heroContent}>
              <h6 style={homeStyles.heroSubtitle}>UNDER FAVORABLE SMARTWATCHES</h6>
              <h1 style={homeStyles.heroTitle}>THE NEW<br/>STANDARD</h1>
              <div style={homeStyles.heroPrice}>FROM $749<sup style={{fontSize: '1.5rem', fontWeight: '400'}}>99</sup></div>
              <Link to="/products" style={homeStyles.heroButton}>
                Start Buying
              </Link>
              
              {/* Slider Navigation Dots */}
              <div style={{
                position: 'absolute',
                bottom: '1rem',
                left: '2rem',
                display: 'flex',
                gap: '0.5rem'
              }}>
                <div style={{
                  width: '12px',
                  height: '12px',
                  borderRadius: '50%',
                  backgroundColor: '#fed700',
                  cursor: 'pointer'
                }}></div>
                <div style={{
                  width: '12px',
                  height: '12px',
                  borderRadius: '50%',
                  backgroundColor: '#bcbcbc',
                  cursor: 'pointer'
                }}></div>
                <div style={{
                  width: '12px',
                  height: '12px',
                  borderRadius: '50%',
                  backgroundColor: '#bcbcbc',
                  cursor: 'pointer'
                }}></div>
              </div>
            </div>
            
            {/* Hero Image */}
            <img 
              src="https://transvelo.github.io/electro-html/2.0/assets/img/416X420/img1.png" 
              alt="Laptop"
              style={homeStyles.heroImage}
            />
          </div>
        </div>
      </section>

      {/* Big Deal Banners */}
      <section style={{ padding: '2rem 0', backgroundColor: '#f8f9fa' }}>
        <div style={{ maxWidth: '1430px', margin: '0 auto', padding: '0 1rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
            {[
              { title: 'CATCH BIG', subtitle: 'DEALS ON THE', highlight: 'CAMERAS', image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg' },
              { title: 'CATCH BIG', subtitle: 'DEALS ON THE', highlight: 'CAMERAS', image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg' },
              { title: 'CATCH BIG', subtitle: 'DEALS ON THE', highlight: 'CAMERAS', image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg' },
              { title: 'CATCH BIG', subtitle: 'DEALS ON THE', highlight: 'CAMERAS', image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg' }
            ].map((banner, index) => (
              <div key={index} style={{
                backgroundColor: 'white',
                padding: '1.5rem',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                gap: '1rem',
                cursor: 'pointer',
                transition: 'transform 0.3s ease'
              }}
              onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-3px)'}
              onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
              >
                <div>
                  <div style={{ 
                    fontSize: '0.7rem', 
                    color: '#6c757d',
                    fontFamily: 'Open Sans, Arial, sans-serif'
                  }}>{banner.title}</div>
                  <div style={{ 
                    fontSize: '0.7rem', 
                    color: '#6c757d',
                    fontFamily: 'Open Sans, Arial, sans-serif'
                  }}>{banner.subtitle}</div>
                  <div style={{ 
                    fontSize: '0.9rem', 
                    fontWeight: '600', 
                    color: '#2c3e50',
                    fontFamily: 'Open Sans, Arial, sans-serif'
                  }}>{banner.highlight}</div>
                  <div style={{ 
                    fontSize: '0.7rem', 
                    color: '#fed700', 
                    fontWeight: '600',
                    fontFamily: 'Open Sans, Arial, sans-serif'
                  }}>Shop now ➤</div>
                </div>
                <img src={banner.image} alt="" style={{ width: '60px', height: '60px', objectFit: 'cover', borderRadius: '8px' }} />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Top Products Section */}
      <section style={{ padding: '3rem 0', backgroundColor: 'white' }}>
        <div style={{ maxWidth: '1430px', margin: '0 auto', padding: '0 1rem' }}>
          <h2 style={{
            fontSize: '1.5rem',
            fontWeight: '600',
            color: '#2c3e50',
            textAlign: 'center',
            marginBottom: '2rem',
            fontFamily: 'Open Sans, Arial, sans-serif'
          }}>
            Top Products This Week
          </h2>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: '1.5rem'
          }}>
            {products.slice(0, 4).map((product) => (
              <SimpleProductCard
                key={product.id}
                product={product}
                onAddToCart={handleAddToCart}
                onAddToWishlist={handleAddToWishlist}
                isInWishlist={isInWishlist}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section style={{ padding: '3rem 0', backgroundColor: '#f8f9fa' }}>
        <div style={{ maxWidth: '1430px', margin: '0 auto', padding: '0 1rem' }}>
          <h2 style={{
            fontSize: '1.5rem',
            fontWeight: '600',
            color: '#2c3e50',
            textAlign: 'center',
            marginBottom: '2rem',
            fontFamily: 'Open Sans, Arial, sans-serif'
          }}>
            Shop by Category
          </h2>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
            gap: '1.5rem'
          }}>
            {categories.map((category, index) => (
              <div
                key={index}
                style={{
                  backgroundColor: 'white',
                  padding: '2rem 1rem',
                  borderRadius: '8px',
                  textAlign: 'center',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  border: '1px solid #e9ecef'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = 'translateY(-5px)';
                  e.currentTarget.style.boxShadow = '0 8px 25px rgba(0,0,0,0.1)';
                  e.currentTarget.style.borderColor = '#fed700';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                  e.currentTarget.style.borderColor = '#e9ecef';
                }}
              >
                <div style={{ 
                  fontSize: '2.5rem', 
                  marginBottom: '1rem' 
                }}>
                  {category.icon}
                </div>
                <h4 style={{
                  fontSize: '0.85rem',
                  fontWeight: '600',
                  color: '#2c3e50',
                  marginBottom: '0.3rem',
                  fontFamily: 'Open Sans, Arial, sans-serif'
                }}>
                  {category.name}
                </h4>
                <p style={{
                  fontSize: '0.7rem',
                  color: '#6c757d',
                  margin: 0,
                  fontFamily: 'Open Sans, Arial, sans-serif'
                }}>
                  {category.count}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products Section */}
      <section style={{ padding: '3rem 0', backgroundColor: 'white' }}>
        <div style={{ maxWidth: '1430px', margin: '0 auto', padding: '0 1rem' }}>
          <h2 style={{
            fontSize: '1.5rem',
            fontWeight: '600',
            color: '#2c3e50',
            textAlign: 'center',
            marginBottom: '2rem',
            fontFamily: 'Open Sans, Arial, sans-serif'
          }}>
            Featured Products
          </h2>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '2rem'
          }}>
            {products.slice(4, 8).map((product) => (
              <SimpleProductCard
                key={product.id}
                product={product}
                onAddToCart={handleAddToCart}
                onAddToWishlist={handleAddToWishlist}
                isInWishlist={isInWishlist}
              />
            ))}
          </div>

          {/* View All Products Button */}
          <div style={{
            textAlign: 'center',
            marginTop: '3rem'
          }}>
            <Link
              to="/products"
              style={{
                backgroundColor: '#2c3e50',
                color: 'white',
                padding: '1rem 3rem',
                borderRadius: '6px',
                textDecoration: 'none',
                fontWeight: '600',
                display: 'inline-block',
                fontSize: '1rem',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                transition: 'all 0.3s ease',
                fontFamily: 'Open Sans, Arial, sans-serif'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = '#1a252f';
                e.currentTarget.style.transform = 'translateY(-3px)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = '#2c3e50';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              View All Products
            </Link>
          </div>
        </div>
      </section>

      {/* Newsletter Section */}
      <section style={{
        backgroundColor: '#fed700',
        padding: '3rem 0'
      }}>
        <div style={{
          maxWidth: '1430px',
          margin: '0 auto',
          padding: '0 1rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <div style={{ fontSize: '3rem' }}>✈️</div>
            <div>
              <h3 style={{ 
                fontSize: '1.8rem', 
                fontWeight: '600', 
                color: '#2c3e50', 
                margin: 0,
                marginBottom: '0.5rem',
                fontFamily: 'Open Sans, Arial, sans-serif'
              }}>
                Sign up to Newsletter
              </h3>
              <p style={{ 
                fontSize: '1.1rem', 
                color: '#2c3e50', 
                margin: 0,
                opacity: 0.8,
                fontFamily: 'Open Sans, Arial, sans-serif'
              }}>
                ...and receive $20 coupon for first shopping.
              </p>
            </div>
          </div>
          
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input 
              type="email" 
              placeholder="Email address" 
              style={{
                padding: '1rem 1.5rem',
                borderRadius: '30px',
                border: 'none',
                fontSize: '1rem',
                minWidth: '300px',
                outline: 'none',
                fontFamily: 'Open Sans, Arial, sans-serif'
              }}
            />
            <button style={{
              backgroundColor: '#2c3e50',
              color: 'white',
              border: 'none',
              padding: '1rem 2rem',
              borderRadius: '30px',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '1rem',
              transition: 'all 0.3s ease',
              fontFamily: 'Open Sans, Arial, sans-serif'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#1a252f'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#2c3e50'}
            >
              Sign Up
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        backgroundColor: '#2c3e50',
        color: 'white',
        padding: '3rem 0 2rem',
        fontFamily: 'Open Sans, Arial, sans-serif'
      }}>
        <div style={{
          maxWidth: '1430px',
          margin: '0 auto',
          padding: '0 1rem',
          textAlign: 'center',
          fontSize: '0.9rem'
        }}>
          © 2024 Electro - All Rights Reserved
        </div>
      </footer>
    </div>
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
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/cart" element={<Cart />} />
                <Route path="/wishlist" element={<Wishlist />} />
                <Route path="/products" element={<Products />} />
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
            </div>
          </Router>
        </ToastProvider>
      </ShopProvider>
    </AuthProvider>
  );
}

export default App;
