import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useShop } from '../contexts/ShopContext';
import { useToast } from '../contexts/ToastContext';
import SimpleProductCard from '../components/SimpleProductCard';
import Recommendations from '../components/Recommendations';

// Home Page Component
const Home = () => {
  const { addToCart, addToWishlist, isInWishlist } = useShop();
  const { showSuccess, showWarning, showWishlist } = useToast();
  
  // Responsive state
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const [isTablet, setIsTablet] = useState(window.innerWidth <= 1024);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
      setIsTablet(window.innerWidth <= 1024);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Inline styles
  const styles = {
    homeContainer: {
      backgroundColor: '#ffffff',
      minHeight: '100vh',
      fontFamily: "'Open Sans', Arial, sans-serif"
    },
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
      padding: '0',
      display: 'flex',
      gap: '0',
      alignItems: 'flex-start',
      flexDirection: isMobile ? 'column' as const : 'row' as const
    },
    heroContent: {
      flex: 1,
      background: '',
      color: 'white',
      padding: isMobile ? '2rem 1rem' : '3rem 2rem',
      borderRadius: '0',
      position: 'relative' as const,
      minHeight: '400px',
      display: 'flex',
      flexDirection: 'column' as const,
      justifyContent: 'center'
    },
    heroTitle: {
      fontSize: isMobile ? '2.5rem' : '3.5rem',
      fontWeight: 700,
      marginBottom: '1rem',
      lineHeight: 1.1,
      letterSpacing: '0.5px',
      fontFamily: "'Open Sans', Arial, sans-serif",
      textTransform: 'uppercase' as const,
      color: '#353E48'
    },
    heroSubtitle: {
      fontSize: '0.8rem',
      marginBottom: '0.5rem',
      opacity: 0.9,
      lineHeight: 1.5,
      fontWeight: 500,
      fontFamily: "'Open Sans', Arial, sans-serif",
      textTransform: 'uppercase' as const,
      letterSpacing: '1.5px',
      color: '#353E48'
    },
    heroPrice: {
      fontSize: isMobile ? '2rem' : '2.5rem',
      fontWeight: 300,
      marginBottom: '2rem',
      color: '#353E48',
      fontFamily: "'Open Sans', Arial, sans-serif"
    },
    heroButton: {
      backgroundColor: '#fed700',
      color: '#333333',
      padding: '0.7rem 1rem',
      borderRadius: '4px',
      textDecoration: 'none',
      fontWeight: 700,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      transition: 'all 0.3s ease',
      border: 'none',
      cursor: 'pointer',
      textTransform: 'uppercase' as const,
      fontFamily: "'Open Sans', Arial, sans-serif",
      fontSize: '0.8rem',
      letterSpacing: '0.3px',
      width: 'auto',
      maxWidth: '130px',
      textAlign: 'center' as const,
      lineHeight: 1,
      minHeight: '35px'
    },
    heroImage: {
      width: isMobile ? '300px' : '400px',
      height: 'auto',
      objectFit: 'contain' as const,
      position: 'absolute' as const,
      right: '1rem',
      top: '50%',
      transform: 'translateY(-50%)',
      display: isMobile ? 'none' : 'block'
    },
    sideNavigation: {
      width: isMobile ? '100%' : '250px',
      backgroundColor: '#f8f9fa',
      padding: '0',
      borderRadius: '0',
      border: '1px solid #e9ecef'
    },
    navItem: {
      padding: '0.6rem 1rem',
      fontWeight: 500,
      color: '#2c3e50',
      borderBottom: '1px solid #e9ecef',
      fontFamily: "'Open Sans', Arial, sans-serif",
      fontSize: '0.75rem',
      textAlign: 'left' as const,
      cursor: 'pointer'
    },
    navItemWithArrow: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    },
    navArrow: {
      fontSize: '0.6rem',
      color: '#6c757d'
    },
    sliderContainer: {
      flex: 1,
      position: 'relative' as const,
      overflow: 'hidden',
      width: '100%'
    },
    sliderWrapper: {
      display: 'flex',
      transition: 'transform 0.5s ease-in-out',
      height: '100%',
      transform: `translateX(-${33.33}%)`
    },
    slide: {
      flexShrink: 0,
      width: '33.33%',
      minWidth: '33.33%'
    },
    navArrowBtn: {
      position: 'absolute' as const,
      top: '50%',
      transform: 'translateY(-50%)',
      backgroundColor: 'rgba(255, 255, 255, 0.8)',
      border: 'none',
      borderRadius: '50%',
      width: '40px',
      height: '40px',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '1.2rem',
      color: '#333',
      transition: 'all 0.3s ease',
      zIndex: 10
    },
    sliderDots: {
      position: 'absolute' as const,
      bottom: '1rem',
      left: '2rem',
      display: 'flex',
      gap: '0.5rem',
      zIndex: 10
    },
    dotBtn: {
      width: '12px',
      height: '12px',
      borderRadius: '50%',
      border: 'none',
      cursor: 'pointer',
      transition: 'all 0.3s ease'
    },
    activeDot: {
      backgroundColor: '#fed700'
    },
    inactiveDot: {
      backgroundColor: '#bcbbbb'
    },
    dotBtnActive: {
      backgroundColor: '#fed700'
    },
    dotBtnInactive: {
      backgroundColor: '#bcbcbc'
    },
    bigDealSection: {
      padding: '2rem 0',
      backgroundColor: '#f8f9fa'
    },
    bigDealContainer: {
      maxWidth: '1430px',
      margin: '0 auto',
      padding: '0 1rem'
    },
    bigDealGrid: {
      display: 'grid',
      gridTemplateColumns: isMobile ? '1fr' : isTablet ? 'repeat(2, 1fr)' : 'repeat(4, 1fr)',
      gap: '1rem'
    },
    dealBanner: {
      backgroundColor: 'white',
      padding: '1.5rem',
      borderRadius: '8px',
      display: 'flex',
      alignItems: 'center',
      gap: '1rem',
      cursor: 'pointer',
      transition: 'transform 0.3s ease'
    },
    dealText: {
      fontSize: '0.7rem',
      color: '#6c757d',
      fontFamily: "'Open Sans', Arial, sans-serif"
    },
    dealHighlight: {
      fontSize: '0.9rem',
      fontWeight: 600,
      color: '#2c3e50',
      fontFamily: "'Open Sans', Arial, sans-serif"
    },
    dealLink: {
      fontSize: '0.7rem',
      color: '#fed700',
      fontWeight: 600,
      fontFamily: "'Open Sans', Arial, sans-serif"
    },
    dealImage: {
      width: '60px',
      height: '60px',
      objectFit: 'cover' as const,
      borderRadius: '8px'
    },
    productsSection: {
      padding: '3rem 0',
      backgroundColor: 'white'
    },
    productsContainer: {
      maxWidth: '1430px',
      margin: '0 auto',
      padding: '0 1rem'
    },
    sectionTitle: {
      fontSize: '1.5rem',
      fontWeight: 600,
      color: '#2c3e50',
      textAlign: 'center' as const,
      marginBottom: '2rem',
      fontFamily: "'Open Sans', Arial, sans-serif"
    },
    productsGrid: {
      display: 'grid',
      gridTemplateColumns: isMobile ? '1fr' : isTablet ? 'repeat(2, 1fr)' : 'repeat(auto-fit, minmax(240px, 1fr))',
      gap: '1.5rem'
    },
    featuredProductsGrid: {
      display: 'grid',
      gridTemplateColumns: isMobile ? '1fr' : isTablet ? 'repeat(2, 1fr)' : 'repeat(auto-fit, minmax(280px, 1fr))',
      gap: '2rem'
    },
    categoriesSection: {
      padding: '3rem 0',
      backgroundColor: '#f8f9fa'
    },
    categoriesGrid: {
      display: 'grid',
      gridTemplateColumns: isMobile ? 'repeat(2, 1fr)' : isTablet ? 'repeat(4, 1fr)' : 'repeat(auto-fit, minmax(140px, 1fr))',
      gap: '1.5rem'
    },
    categoryCard: {
      backgroundColor: 'white',
      padding: '2rem 1rem',
      borderRadius: '8px',
      textAlign: 'center' as const,
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      border: '1px solid #e9ecef'
    },
    categoryIcon: {
      fontSize: '2.5rem',
      marginBottom: '1rem'
    },
    categoryName: {
      fontSize: '0.85rem',
      fontWeight: 600,
      color: '#2c3e50',
      marginBottom: '0.3rem',
      fontFamily: "'Open Sans', Arial, sans-serif"
    },
    categoryCount: {
      fontSize: '0.7rem',
      color: '#6c757d',
      margin: '0',
      fontFamily: "'Open Sans', Arial, sans-serif"
    },
    viewAllContainer: {
      textAlign: 'center' as const,
      marginTop: '3rem'
    },
    viewAllBtn: {
      backgroundColor: '#2c3e50',
      color: 'white',
      padding: '1rem 3rem',
      borderRadius: '6px',
      textDecoration: 'none',
      fontWeight: 600,
      display: 'inline-block',
      fontSize: '1rem',
      textTransform: 'uppercase' as const,
      letterSpacing: '0.5px',
      transition: 'all 0.3s ease',
      fontFamily: "'Open Sans', Arial, sans-serif"
    },
    newsletterSection: {
      backgroundColor: '#fed700',
      padding: '3rem 0'
    },
    newsletterContainer: {
      maxWidth: '1430px',
      margin: '0 auto',
      padding: '0 1rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexDirection: isMobile ? 'column' as const : 'row' as const,
      gap: isMobile ? '2rem' : '0'
    },
    newsletterContent: {
      display: 'flex',
      alignItems: 'center',
      gap: '1.5rem',
      flexDirection: isMobile ? 'column' as const : 'row' as const,
      textAlign: isMobile ? 'center' as const : 'left' as const
    },
    newsletterIcon: {
      fontSize: '3rem'
    },
    newsletterTitle: {
      fontSize: isMobile ? '1.5rem' : '1.8rem',
      fontWeight: 600,
      color: '#2c3e50',
      margin: '0',
      marginBottom: '0.5rem',
      fontFamily: "'Open Sans', Arial, sans-serif"
    },
    newsletterSubtitle: {
      fontSize: '1.1rem',
      color: '#2c3e50',
      margin: '0',
      opacity: 0.8,
      fontFamily: "'Open Sans', Arial, sans-serif"
    },
    newsletterForm: {
      display: 'flex',
      gap: '0.5rem',
      flexDirection: isMobile ? 'column' as const : 'row' as const,
      width: isMobile ? '100%' : 'auto'
    },
    newsletterInput: {
      padding: '1rem 1.5rem',
      borderRadius: '30px',
      border: 'none',
      fontSize: '1rem',
      minWidth: isMobile ? '100%' : '300px',
      outline: 'none',
      fontFamily: "'Open Sans', Arial, sans-serif"
    },
    newsletterBtn: {
      backgroundColor: '#2c3e50',
      color: 'white',
      border: 'none',
      padding: '1rem 2rem',
      borderRadius: '30px',
      cursor: 'pointer',
      fontWeight: 600,
      fontSize: '1rem',
      transition: 'all 0.3s ease',
      fontFamily: "'Open Sans', Arial, sans-serif"
    },
    footer: {
      backgroundColor: '#2c3e50',
      color: 'white',
      padding: '3rem 0 2rem',
      fontFamily: "'Open Sans', Arial, sans-serif"
    },
    footerContainer: {
      maxWidth: '1430px',
      margin: '0 auto',
      padding: '0 1rem',
      textAlign: 'center' as const,
      fontSize: '0.9rem'
    }
  };
  
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
    <div style={styles.homeContainer}>
      {/* Hero Banner với Slider */}
      <section style={styles.heroBanner}>
        <div style={styles.heroContainer}>
          {/* Side Navigation */}
          <div style={styles.sideNavigation}>
            <div style={styles.navItem}>
              Value of the Day
            </div>
            <div style={styles.navItem}>
              Top 100 Offers
            </div>
            <div style={styles.navItem}>
              New Arrivals
            </div>
            <div style={{...styles.navItem, ...styles.navItemWithArrow}}>
              <span>Computers & Accessories</span>
              <span style={styles.navArrow}>→</span>
            </div>
            <div style={{...styles.navItem, ...styles.navItemWithArrow}}>
              <span>Cameras, Audio & Video</span>
              <span style={styles.navArrow}>→</span>
            </div>
            <div style={{...styles.navItem, ...styles.navItemWithArrow}}>
              <span>Mobiles & Tablets</span>
              <span style={styles.navArrow}>→</span>
            </div>
            <div style={{...styles.navItem, ...styles.navItemWithArrow}}>
              <span>Movies, Music & Video Game</span>
              <span style={styles.navArrow}>→</span>
            </div>
            <div style={{...styles.navItem, ...styles.navItemWithArrow}}>
              <span>TV & Audio</span>
              <span style={styles.navArrow}>→</span>
            </div>
            <div style={{...styles.navItem, ...styles.navItemWithArrow}}>
              <span>Watches & Eyewear</span>
              <span style={styles.navArrow}>→</span>
            </div>
            <div style={{...styles.navItem, ...styles.navItemWithArrow}}>
              <span>Car, Motorbike & Industrial</span>
              <span style={styles.navArrow}>→</span>
            </div>
            <div style={{...styles.navItem, ...styles.navItemWithArrow}}>
              <span>Accessories</span>
              <span style={styles.navArrow}>→</span>
            </div>
          </div>
          
          {/* Main Hero Content - Slider */}
          <div style={styles.sliderContainer}>
            {/* Slider Container */}
            <div 
              style={{
                ...styles.sliderWrapper,
                transform: `translateX(-${currentSlide * (100 / slides.length)}%)`,
                width: `${slides.length * 100}%`
              }}
            >
              {slides.map((slide, index) => (
                <div key={slide.id} style={{...styles.heroContent, ...styles.slide}}>
                  <h6 style={styles.heroSubtitle}>{slide.subtitle}</h6>
                  <h1 style={styles.heroTitle}>{slide.title.split('\n').map((line, i) => (
                    <React.Fragment key={i}>
                      {line}
                      {i < slide.title.split('\n').length - 1 && <br />}
                    </React.Fragment>
                  ))}</h1>
                  <div style={styles.heroPrice}>
                    {slide.price}<sup>{slide.superscript}</sup>
                  </div>
                  <Link to={slide.buttonLink} style={styles.heroButton}>
                    {slide.buttonText}
                  </Link>
                  
                  {/* Hero Image for current slide */}
                  <img 
                    src={slide.image} 
                    alt={`Slide ${index + 1}`}
                    style={styles.heroImage}
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
            <div style={styles.sliderDots}>
              {slides.map((_, index) => (
                <button
                  key={index}
                  onClick={() => goToSlide(index)}
                  style={{
                    ...(styles.dotBtn),
                    ...(currentSlide === index ? styles.activeDot : styles.inactiveDot)
                  }}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Big Deal Banners */}
      <section style={styles.bigDealSection}>
        <div style={styles.bigDealContainer}>
          <div style={styles.bigDealGrid}>
            {[
              { title: 'CATCH BIG', subtitle: 'DEALS ON THE', highlight: 'CAMERAS', image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg' },
              { title: 'CATCH BIG', subtitle: 'DEALS ON THE', highlight: 'CAMERAS', image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg' },
              { title: 'CATCH BIG', subtitle: 'DEALS ON THE', highlight: 'CAMERAS', image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg' },
              { title: 'CATCH BIG', subtitle: 'DEALS ON THE', highlight: 'CAMERAS', image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg' }
            ].map((banner, index) => (
              <div key={index} style={styles.dealBanner}>
                <div>
                  <div style={styles.dealText}>{banner.title}</div>
                  <div style={styles.dealText}>{banner.subtitle}</div>
                  <div style={styles.dealHighlight}>{banner.highlight}</div>
                  <div style={styles.dealLink}>Shop now ➤</div>
                </div>
                <img src={banner.image} alt="" style={styles.dealImage} />
              </div>
            ))}
          </div>
        </div>
      </section>
       {/* Recommendations Section */}


      <section style={styles.productsSection}>
        <div style={styles.productsContainer}>
          <Recommendations 
            limit={4} 
            title="Recommended for You"
            className=""
          />
        </div>


      </section>
      {/* Top Products Section */}
      <section style={styles.productsSection}>
        <div style={styles.productsContainer}>
          <h2 style={styles.sectionTitle}>
            Top Products This Week
          </h2>
          
          <div style={styles.productsGrid}>
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
      <section style={styles.categoriesSection}>
        <div style={styles.productsContainer}>
          <h2 style={styles.sectionTitle}>
            Shop by Category
          </h2>
          
          <div style={styles.categoriesGrid}>
            {categories.map((category, index) => (
              <div key={index} style={styles.categoryCard}>
                <div style={styles.categoryIcon}>
                  {category.icon}
                </div>
                <h4 style={styles.categoryName}>
                  {category.name}
                </h4>
                <p style={styles.categoryCount}>
                  {category.count}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products Section */}
      <section style={styles.productsSection}>
        <div style={styles.productsContainer}>
          <h2 style={styles.sectionTitle}>
            Featured Products
          </h2>
          
          <div style={styles.featuredProductsGrid}>
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
          <div style={styles.viewAllContainer}>
            <Link to="/products" style={styles.viewAllBtn}>
              View All Products
            </Link>
          </div>
        </div>
      </section>

      {/* Newsletter Section */}
      <section style={styles.newsletterSection}>
        <div style={styles.newsletterContainer}>
          <div style={styles.newsletterContent}>
            <div style={styles.newsletterIcon}>✈️</div>
            <div>
              <h3 style={styles.newsletterTitle}>
                Sign up to Newsletter
              </h3>
              <p style={styles.newsletterSubtitle}>
                ...and receive $20 coupon for first shopping.
              </p>
            </div>
          </div>
          
          <div style={styles.newsletterForm}>
            <input 
              type="email" 
              placeholder="Email address" 
              style={styles.newsletterInput}
            />
            <button style={styles.newsletterBtn}>
              Sign Up
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={styles.footer}>
        <div style={styles.footerContainer}>
          © 2024 Electro - All Rights Reserved
        </div>
      </footer>
    </div>
  );
};

export default Home;