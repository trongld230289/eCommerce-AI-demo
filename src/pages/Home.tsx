import React from 'react';
import { Link } from 'react-router-dom';
import { useShop } from '../contexts/ShopContext';
import type { Product } from '../contexts/ShopContext';
import SimpleProductCard from '../components/SimpleProductCard';

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

  // Electro theme color palette
  const colors = {
    primary: '#0066cc',
    secondary: '#ff6b35',
    dark: '#2c3e50',
    light: '#ecf0f1',
    success: '#27ae60',
    warning: '#f39c12',
    danger: '#e74c3c'
  };

  return (
    <div style={{ backgroundColor: '#f8f9fa', minHeight: '100vh' }}>
      {/* Hero Banner Section - Electro Style */}
      <section style={{
        background: `linear-gradient(135deg, ${colors.primary} 0%, #004499 100%)`,
        color: 'white',
        padding: '80px 20px',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{ 
          maxWidth: '1200px', 
          margin: '0 auto',
          position: 'relative',
          zIndex: 2
        }}>
          <div style={{ marginBottom: '20px' }}>
            <span style={{
              backgroundColor: colors.secondary,
              padding: '8px 20px',
              borderRadius: '20px',
              fontSize: '14px',
              fontWeight: 'bold',
              textTransform: 'uppercase',
              letterSpacing: '1px'
            }}>
              THE NEW STANDARD
            </span>
          </div>
          <h1 style={{ 
            fontSize: '4rem', 
            fontWeight: '800', 
            marginBottom: '20px',
            lineHeight: '1.2',
            textShadow: '0 2px 4px rgba(0,0,0,0.3)'
          }}>
            PREMIUM ELECTRONICS
          </h1>
          <h2 style={{
            fontSize: '1.8rem',
            fontWeight: '400',
            marginBottom: '30px',
            opacity: 0.9
          }}>
            Under Favorable Prices
          </h2>
          <p style={{ 
            fontSize: '1.2rem', 
            marginBottom: '40px', 
            opacity: 0.8,
            maxWidth: '600px',
            margin: '0 auto 40px'
          }}>
            Discover the latest in technology with unbeatable prices and premium quality
          </p>
          <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link
              to="/products"
              style={{
                backgroundColor: colors.secondary,
                color: 'white',
                padding: '15px 40px',
                borderRadius: '8px',
                fontWeight: 'bold',
                fontSize: '16px',
                textDecoration: 'none',
                display: 'inline-block',
                transition: 'all 0.3s ease',
                boxShadow: '0 4px 15px rgba(0,0,0,0.2)'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = '#e55a2b';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = colors.secondary;
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              Start Shopping
            </Link>
            <Link
              to="/products"
              style={{
                backgroundColor: 'transparent',
                color: 'white',
                padding: '15px 40px',
                borderRadius: '8px',
                fontWeight: 'bold',
                fontSize: '16px',
                textDecoration: 'none',
                display: 'inline-block',
                border: '2px solid white',
                transition: 'all 0.3s ease'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = 'white';
                e.currentTarget.style.color = colors.primary;
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = 'white';
              }}
            >
              View Catalog
            </Link>
          </div>
        </div>
        {/* Background decorative elements */}
        <div style={{
          position: 'absolute',
          top: '-50px',
          right: '-50px',
          width: '200px',
          height: '200px',
          backgroundColor: 'rgba(255,255,255,0.1)',
          borderRadius: '50%',
          zIndex: 1
        }}></div>
        <div style={{
          position: 'absolute',
          bottom: '-30px',
          left: '-30px',
          width: '150px',
          height: '150px',
          backgroundColor: 'rgba(255,255,255,0.05)',
          borderRadius: '50%',
          zIndex: 1
        }}></div>
      </section>

      {/* Featured Categories Section */}
      <section style={{ 
        padding: '60px 20px',
        backgroundColor: 'white'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '50px' }}>
            <h2 style={{ 
              fontSize: '2.5rem', 
              fontWeight: '700', 
              color: colors.dark,
              marginBottom: '15px'
            }}>
              Shop by Category
            </h2>
            <p style={{ 
              fontSize: '1.1rem', 
              color: '#7f8c8d',
              maxWidth: '600px',
              margin: '0 auto'
            }}>
              Browse our extensive collection of premium electronics
            </p>
          </div>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '30px'
          }}>
            {[
              { icon: '🎧', title: 'Audio & Headphones', count: '250+ Products' },
              { icon: '💻', title: 'Laptops & Computers', count: '180+ Products' },
              { icon: '📱', title: 'Smartphones', count: '120+ Products' },
              { icon: '⌚', title: 'Smart Watches', count: '90+ Products' }
            ].map((category, index) => (
              <Link
                key={index}
                to="/products"
                style={{
                  display: 'block',
                  textAlign: 'center',
                  padding: '40px 20px',
                  backgroundColor: '#f8f9fa',
                  borderRadius: '12px',
                  textDecoration: 'none',
                  color: colors.dark,
                  transition: 'all 0.3s ease',
                  border: '2px solid transparent'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.borderColor = colors.primary;
                  e.currentTarget.style.transform = 'translateY(-5px)';
                  e.currentTarget.style.boxShadow = '0 10px 30px rgba(0,0,0,0.1)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.borderColor = 'transparent';
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <div style={{ fontSize: '4rem', marginBottom: '20px' }}>
                  {category.icon}
                </div>
                <h3 style={{ 
                  fontSize: '1.3rem', 
                  fontWeight: '600', 
                  marginBottom: '10px',
                  color: colors.dark
                }}>
                  {category.title}
                </h3>
                <p style={{ color: '#7f8c8d', fontSize: '0.9rem' }}>
                  {category.count}
                </p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products Section - Electro Style */}
      <section style={{ 
        padding: '60px 20px',
        backgroundColor: '#f8f9fa'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            marginBottom: '50px',
            flexWrap: 'wrap',
            gap: '20px'
          }}>
            <div>
              <h2 style={{ 
                fontSize: '2.5rem', 
                fontWeight: '700', 
                color: colors.dark,
                marginBottom: '10px'
              }}>
                Featured Products
              </h2>
              <p style={{ color: '#7f8c8d', fontSize: '1.1rem' }}>
                Best deals on premium electronics
              </p>
            </div>
            <Link
              to="/products"
              style={{ 
                color: colors.primary, 
                textDecoration: 'none', 
                fontWeight: '600',
                fontSize: '1.1rem',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}
            >
              View All Products →
            </Link>
          </div>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
            gap: '2rem' 
          }}>
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
      <section style={{ 
        padding: '60px 20px',
        backgroundColor: colors.dark,
        color: 'white'
      }}>
        <div style={{ 
          maxWidth: '1200px', 
          margin: '0 auto',
          textAlign: 'center'
        }}>
          <div style={{ marginBottom: '20px' }}>
            <span style={{
              backgroundColor: colors.warning,
              color: 'white',
              padding: '8px 20px',
              borderRadius: '20px',
              fontSize: '14px',
              fontWeight: 'bold',
              textTransform: 'uppercase'
            }}>
              Special Offer
            </span>
          </div>
          <h2 style={{ 
            fontSize: '3rem', 
            fontWeight: '700', 
            marginBottom: '20px' 
          }}>
            Save up to 50% on Electronics
          </h2>
          <p style={{ 
            fontSize: '1.2rem', 
            marginBottom: '30px', 
            opacity: 0.9,
            maxWidth: '600px',
            margin: '0 auto 30px'
          }}>
            Limited time offer on selected premium electronics. Don't miss out!
          </p>
          <Link
            to="/products"
            style={{
              backgroundColor: colors.secondary,
              color: 'white',
              padding: '15px 40px',
              borderRadius: '8px',
              fontWeight: 'bold',
              fontSize: '16px',
              textDecoration: 'none',
              display: 'inline-block',
              transition: 'all 0.3s ease'
            }}
          >
            Shop Now & Save
          </Link>
        </div>
      </section>

      {/* Trust Indicators - Electro Style */}
      <section style={{ 
        padding: '60px 20px',
        backgroundColor: 'white'
      }}>
        <div style={{ 
          maxWidth: '1200px', 
          margin: '0 auto'
        }}>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
            gap: '40px'
          }}>
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
              <div key={index} style={{ 
                textAlign: 'center', 
                padding: '30px 20px',
                borderRadius: '12px',
                transition: 'all 0.3s ease'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = '#f8f9fa';
                e.currentTarget.style.transform = 'translateY(-5px)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
              >
                <div style={{ 
                  fontSize: '3.5rem', 
                  marginBottom: '20px'
                }}>
                  {feature.icon}
                </div>
                <h3 style={{ 
                  fontSize: '1.3rem', 
                  fontWeight: '600', 
                  marginBottom: '10px',
                  color: colors.dark
                }}>
                  {feature.title}
                </h3>
                <p style={{ 
                  color: '#7f8c8d',
                  lineHeight: '1.5'
                }}>
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
