import React from 'react';
import { Link } from 'react-router-dom';
import { useShop } from '../contexts/ShopContext';
import type { Product } from '../contexts/ShopContext';
import SimpleProductCard from '../components/SimpleProductCard';
import './Home.css';

const Home: React.FC = () => {
  // Sample featured products data
  const featuredProducts: Product[] = [
    {
      id: 1,
      name: 'Wireless Headphones Pro Max',
      price: 299.99,
      image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500',
      category: 'Electronics',
      description: 'Premium wireless headphones with active noise cancellation and 30-hour battery life'
    },
    {
      id: 2,
      name: 'Smart Watch Series 8',
      price: 399.99,
      image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500',
      category: 'Electronics',
      description: 'Advanced smartwatch with health monitoring, GPS, and cellular connectivity'
    },
    {
      id: 3,
      name: 'Gaming Laptop Ultra',
      price: 1299.99,
      image: 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500',
      category: 'Electronics',
      description: 'High-performance gaming laptop with RTX graphics and 144Hz display'
    },
    {
      id: 4,
      name: 'Smartphone Pro 15',
      price: 899.99,
      image: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500',
      category: 'Electronics',
      description: 'Latest smartphone with triple camera system and A17 Bionic chip'
    },
    {
      id: 5,
      name: 'Bluetooth Speaker Premium',
      price: 149.99,
      image: 'https://images.unsplash.com/photo-1545454675-3531b543be5d?w=500',
      category: 'Electronics',
      description: 'Portable bluetooth speaker with 360-degree sound and waterproof design'
    },
    {
      id: 6,
      name: 'Gaming Mouse RGB',
      price: 79.99,
      image: 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500',
      category: 'Electronics',
      description: 'Professional gaming mouse with 16000 DPI sensor and customizable RGB lighting'
    }
  ];

  const { addToCart, addToWishlist, isInWishlist } = useShop();

  return (
    <div className="home-container">
      {/* Hero Banner Section - Electro Style */}
      <section className="hero-section">
        <div className="hero-content">
          <div>
            <span className="hero-badge">
              THE NEW STANDARD
            </span>
          </div>
          <h1 className="hero-title">
            PREMIUM ELECTRONICS
          </h1>
          <h2 className="hero-subtitle">
            Under Favorable Prices
          </h2>
          <p className="hero-description">
            Discover the latest in technology with unbeatable prices and premium quality
          </p>
          <div className="hero-buttons">
            <Link
              to="/products"
              className="btn-primary"
            >
              Start Shopping
            </Link>
            <Link
              to="/products"
              className="btn-secondary"
            >
              View Catalog
            </Link>
          </div>
        </div>
        {/* Background decorative elements */}
        <div className="hero-decoration-1"></div>
        <div className="hero-decoration-2"></div>
      </section>

      {/* Featured Categories Section */}
      <section className="section section-white">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">
              Shop by Category
            </h2>
            <p className="section-subtitle">
              Browse our extensive collection of premium electronics
            </p>
          </div>
          
          <div className="categories-grid">
            {[
              { icon: '🎧', title: 'Audio & Headphones', count: '250+ Products' },
              { icon: '💻', title: 'Laptops & Computers', count: '180+ Products' },
              { icon: '📱', title: 'Smartphones', count: '120+ Products' },
              { icon: '⌚', title: 'Smart Watches', count: '90+ Products' }
            ].map((category, index) => (
              <Link
                key={index}
                to="/products"
                className="category-card"
              >
                <div className="category-icon">
                  {category.icon}
                </div>
                <h3 className="category-title">
                  {category.title}
                </h3>
                <p className="category-count">
                  {category.count}
                </p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products Section - Electro Style */}
      <section className="section section-gray">
        <div className="container">
          <div className="featured-header">
            <div className="featured-info">
              <h2>
                Featured Products
              </h2>
              <p>
                Best deals on premium electronics
              </p>
            </div>
            <Link
              to="/products"
              className="view-all-link"
            >
              View All Products →
            </Link>
          </div>
          
          <div className="products-grid">
            {featuredProducts.map((product: Product) => (
              <SimpleProductCard
                key={product.id}
                product={product}
                onAddToCart={addToCart}
                onAddToWishlist={addToWishlist}
                isInWishlist={isInWishlist}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Special Offer Banner */}
      <section className="section section-dark">
        <div className="container offer-section">
          <div>
            <span className="offer-badge">
              Special Offer
            </span>
          </div>
          <h2 className="offer-title">
            Save up to 50% on Electronics
          </h2>
          <p className="offer-description">
            Limited time offer on selected premium electronics. Don't miss out!
          </p>
          <Link
            to="/products"
            className="offer-button"
          >
            Shop Now & Save
          </Link>
        </div>
      </section>

      {/* Trust Indicators - Electro Style */}
      <section className="section section-white">
        <div className="container">
          <div className="trust-grid">
            {[
              { 
                icon: '🚚', 
                title: 'Free Shipping', 
                desc: 'Free shipping on orders over $99'
              },
              { 
                icon: '🔒', 
                title: 'Secure Payment', 
                desc: '100% secure payment processing'
              },
              { 
                icon: '↩️', 
                title: '30-Day Returns', 
                desc: 'Easy returns within 30 days'
              },
              { 
                icon: '🎧', 
                title: '24/7 Support', 
                desc: 'Round-the-clock customer support'
              }
            ].map((feature, index) => (
              <div key={index} className="trust-item">
                <div className="trust-icon">
                  {feature.icon}
                </div>
                <h3 className="trust-title">
                  {feature.title}
                </h3>
                <p className="trust-description">
                  {feature.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
