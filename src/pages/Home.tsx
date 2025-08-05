import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useShop } from '../contexts/ShopContext';
import { useToast } from '../contexts/ToastContext';
import SimpleProductCard from '../components/SimpleProductCard';
import './Home.css';

// Home Page Component
const Home = () => {
  const { addToCart, addToWishlist, isInWishlist } = useShop();
  const { showSuccess, showWarning, showWishlist } = useToast();
  
  // Slider state
  const [currentSlide, setCurrentSlide] = useState(0);
  
  // Slider data
  const slides = [
    {
      id: 1,
      subtitle: "UNDER FAVORABLE SMARTWATCHES",
      title: "THE NEW\nSTANDARD",
      price: "FROM $749",
      superscript: "99",
      image: "https://transvelo.github.io/electro-html/2.0/assets/img/416X420/img1.png",
      buttonText: "Start Buying",
      buttonLink: "/products"
    },
    {
      id: 2,
      subtitle: "WIRELESS AUDIO EXPERIENCE",
      title: "PREMIUM\nSOUND",
      price: "FROM $299",
      superscript: "99",
      image: "https://transvelo.github.io/electro-html/2.0/assets/img/416X420/img2.png",
      buttonText: "Shop Audio",
      buttonLink: "/products?category=headphones"
    },
    {
      id: 3,
      subtitle: "PROFESSIONAL GAMING SETUP",
      title: "GAMING\nREVOLUTION",
      price: "FROM $999",
      superscript: "99",
      image: "https://transvelo.github.io/electro-html/2.0/assets/img/416X420/img3.png",
      buttonText: "Explore Gaming",
      buttonLink: "/products?category=gaming"
    }
  ];

  // Auto-slide functionality
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length);
    }, 5000); // Change slide every 5 seconds

    return () => clearInterval(timer);
  }, [slides.length, currentSlide]); // Reset timer when currentSlide changes

  const goToSlide = (index: number) => {
    setCurrentSlide(index);
    // Timer will automatically reset due to useEffect dependency
  };

  const goToPrevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);
    // Timer will automatically reset due to useEffect dependency
  };

  const goToNextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % slides.length);
    // Timer will automatically reset due to useEffect dependency
  };
  
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
      showWishlist(`Added to Wishlist!`, `${product.name} has been added to your wishlist.`);
    }
  };

  return (
    <div className="home-container">
      {/* Hero Banner với Slider */}
      <section className="hero-banner">
        <div className="hero-container">
          {/* Side Navigation */}
          <div className="side-navigation">
            <div className="nav-item">
              Value of the Day
            </div>
            <div className="nav-item">
              Top 100 Offers
            </div>
            <div className="nav-item">
              New Arrivals
            </div>
            <div className="nav-item nav-item-with-arrow">
              <span>Computers & Accessories</span>
              <span className="nav-arrow">→</span>
            </div>
            <div className="nav-item nav-item-with-arrow">
              <span>Cameras, Audio & Video</span>
              <span className="nav-arrow">→</span>
            </div>
            <div className="nav-item nav-item-with-arrow">
              <span>Mobiles & Tablets</span>
              <span className="nav-arrow">→</span>
            </div>
            <div className="nav-item nav-item-with-arrow">
              <span>Movies, Music & Video Game</span>
              <span className="nav-arrow">→</span>
            </div>
            <div className="nav-item nav-item-with-arrow">
              <span>TV & Audio</span>
              <span className="nav-arrow">→</span>
            </div>
            <div className="nav-item nav-item-with-arrow">
              <span>Watches & Eyewear</span>
              <span className="nav-arrow">→</span>
            </div>
            <div className="nav-item nav-item-with-arrow">
              <span>Car, Motorbike & Industrial</span>
              <span className="nav-arrow">→</span>
            </div>
            <div className="nav-item nav-item-with-arrow">
              <span>Accessories</span>
              <span className="nav-arrow">→</span>
            </div>
          </div>
          
          {/* Main Hero Content - Slider */}
          <div className="slider-container">
            {/* Slider Container */}
            <div 
              className="slider-wrapper"
              style={{
                transform: `translateX(-${currentSlide * (100 / slides.length)}%)`,
                width: `${slides.length * 100}%`
              }}
            >
              {slides.map((slide, index) => (
                <div key={slide.id} className="hero-content slide">
                  <h6 className="hero-subtitle">{slide.subtitle}</h6>
                  <h1 className="hero-title">{slide.title.split('\n').map((line, i) => (
                    <React.Fragment key={i}>
                      {line}
                      {i < slide.title.split('\n').length - 1 && <br />}
                    </React.Fragment>
                  ))}</h1>
                  <div className="hero-price">
                    {slide.price}<sup>{slide.superscript}</sup>
                  </div>
                  <Link to={slide.buttonLink} className="hero-button">
                    {slide.buttonText}
                  </Link>
                  
                  {/* Hero Image for current slide */}
                  <img 
                    src={slide.image} 
                    alt={`Slide ${index + 1}`}
                    className="hero-image"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = `https://via.placeholder.com/400x420/fed700/333333?text=Product+${index + 1}`;
                    }}
                  />
                </div>
              ))}
            </div>
            
            {/* Navigation Arrows */}
            {/* <button
              onClick={goToPrevSlide}
              className="nav-arrow-btn prev"
            >
              ❮
            </button>
            
            <button
              onClick={goToNextSlide}
              className="nav-arrow-btn next"
            >
              ❯
            </button> */}
            
            {/* Slider Navigation Dots */}
            <div className="slider-dots">
              {slides.map((_, index) => (
                <button
                  key={index}
                  onClick={() => goToSlide(index)}
                  className={`dot-btn ${currentSlide === index ? 'active' : 'inactive'}`}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Big Deal Banners */}
      <section className="big-deal-section">
        <div className="big-deal-container">
          <div className="big-deal-grid">
            {[
              { title: 'CATCH BIG', subtitle: 'DEALS ON THE', highlight: 'CAMERAS', image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg' },
              { title: 'CATCH BIG', subtitle: 'DEALS ON THE', highlight: 'CAMERAS', image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg' },
              { title: 'CATCH BIG', subtitle: 'DEALS ON THE', highlight: 'CAMERAS', image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg' },
              { title: 'CATCH BIG', subtitle: 'DEALS ON THE', highlight: 'CAMERAS', image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg' }
            ].map((banner, index) => (
              <div key={index} className="deal-banner">
                <div>
                  <div className="deal-text">{banner.title}</div>
                  <div className="deal-text">{banner.subtitle}</div>
                  <div className="deal-highlight">{banner.highlight}</div>
                  <div className="deal-link">Shop now ➤</div>
                </div>
                <img src={banner.image} alt="" className="deal-image" />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Top Products Section */}
      <section className="products-section">
        <div className="products-container">
          <h2 className="section-title">
            Top Products This Week
          </h2>
          
          <div className="products-grid">
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
      <section className="categories-section">
        <div className="products-container">
          <h2 className="section-title">
            Shop by Category
          </h2>
          
          <div className="categories-grid">
            {categories.map((category, index) => (
              <div key={index} className="category-card">
                <div className="category-icon">
                  {category.icon}
                </div>
                <h4 className="category-name">
                  {category.name}
                </h4>
                <p className="category-count">
                  {category.count}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products Section */}
      <section className="products-section">
        <div className="products-container">
          <h2 className="section-title">
            Featured Products
          </h2>
          
          <div className="featured-products-grid">
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
          <div className="view-all-container">
            <Link to="/products" className="view-all-btn">
              View All Products
            </Link>
          </div>
        </div>
      </section>

      {/* Newsletter Section */}
      <section className="newsletter-section">
        <div className="newsletter-container">
          <div className="newsletter-content">
            <div className="newsletter-icon">✈️</div>
            <div>
              <h3 className="newsletter-title">
                Sign up to Newsletter
              </h3>
              <p className="newsletter-subtitle">
                ...and receive $20 coupon for first shopping.
              </p>
            </div>
          </div>
          
          <div className="newsletter-form">
            <input 
              type="email" 
              placeholder="Email address" 
              className="newsletter-input"
            />
            <button className="newsletter-btn">
              Sign Up
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-container">
          © 2024 Electro - All Rights Reserved
        </div>
      </footer>
    </div>
  );
};

export default Home;
