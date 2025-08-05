import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useShop } from '../contexts/ShopContext';
import type { Product } from '../contexts/ShopContext';
import SimpleProductCard from '../components/SimpleProductCard';
import Recommendations from '../components/Recommendations';
import { searchService } from '../services/searchService';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch, faSpinner } from '@fortawesome/free-solid-svg-icons';
import './Products.css';

const Products: React.FC = () => {
  const { addToCart, addToWishlist, isInWishlist } = useShop();
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [chatbotSearch, setChatbotSearch] = useState<{
    query: string;
    category?: string;
    brand?: string;
    minPrice?: number;
    maxPrice?: number;
  } | null>(null);
  const [backendResults, setBackendResults] = useState<any[]>([]);
  const [isLoadingBackend, setIsLoadingBackend] = useState(false);
  const [backendError, setBackendError] = useState<string | null>(null);

  // Initialize from URL parameters
  useEffect(() => {
    const query = searchParams.get('q') || '';
    const category = searchParams.get('category') || 'All';
    const brand = searchParams.get('brand') || '';
    const minPrice = searchParams.get('minPrice');
    const maxPrice = searchParams.get('maxPrice');
    const chatbotQuery = searchParams.get('chatbot');

    setSearchQuery(query);
    setSelectedCategory(category);

    // If this is a chatbot-initiated search
    if (chatbotQuery) {
      setChatbotSearch({
        query: chatbotQuery,
        category: category !== 'All' ? category : undefined,
        brand: brand || undefined,
        minPrice: minPrice ? parseFloat(minPrice) : undefined,
        maxPrice: maxPrice ? parseFloat(maxPrice) : undefined,
      });
    }
  }, [searchParams]);

  // Fetch backend results when chatbot search is set
  useEffect(() => {
    if (chatbotSearch) {
      fetchBackendResults();
    }
  }, [chatbotSearch]);

  const fetchBackendResults = async () => {
    if (!chatbotSearch) return;

    setIsLoadingBackend(true);
    setBackendError(null);

    try {
      const results = await searchService.searchProducts({
        category: chatbotSearch.category,
        brand: chatbotSearch.brand,
        min_price: chatbotSearch.minPrice,
        max_price: chatbotSearch.maxPrice,
        keywords: chatbotSearch.query
      });

      setBackendResults(results);
    } catch (error) {
      console.error('Error fetching backend results:', error);
      setBackendError('Failed to load search results from server');
    } finally {
      setIsLoadingBackend(false);
    }
  };

  // Convert backend Product to frontend Product format
  const convertBackendProduct = (backendProduct: any): Product => {
    return {
      id: parseInt(backendProduct.id),
      name: backendProduct.name,
      price: backendProduct.price / 100, // Convert from VND cents to dollars equivalent
      originalPrice: undefined,
      image: backendProduct.image,
      category: backendProduct.category,
      description: backendProduct.description,
      brand: backendProduct.brand,
      tags: [],
      rating: backendProduct.rating,
      isNew: false,
      discount: 0
    };
  };

  // Popular search suggestions
  const searchSuggestions = [
    'wireless headphones', 'gaming laptop', 'smartphone', 'rgb keyboard',
    'bluetooth speaker', 'smart watch', 'gaming mouse', 'tablet'
  ];

  // Filter suggestions based on current search
  const filteredSuggestions = searchSuggestions.filter(suggestion =>
    suggestion.toLowerCase().includes(searchQuery.toLowerCase()) &&
    searchQuery.length > 0 &&
    suggestion.toLowerCase() !== searchQuery.toLowerCase()
  );

  // Sample products data with enhanced search properties
  const allProducts: Product[] = [
    {
      id: 1,
      name: 'Wireless Headphones',
      price: 99.99,
      originalPrice: 129.99,
      image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500',
      category: 'Electronics',
      description: 'High-quality wireless headphones with noise cancellation',
      brand: 'AudioTech',
      tags: ['wireless', 'bluetooth', 'noise-cancellation', 'music'],
      color: 'Black',
      rating: 4.5,
      isNew: true,
      discount: 30
    },
    {
      id: 2,
      name: 'Smart Watch',
      price: 299.99,
      originalPrice: 349.99,
      image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500',
      category: 'Electronics',
      description: 'Advanced smartwatch with health monitoring and GPS',
      brand: 'TechWatch',
      tags: ['smartwatch', 'fitness', 'health', 'gps', 'waterproof'],
      color: 'Silver',
      rating: 4.7,
      discount: 50
    },
    {
      id: 3,
      name: 'Gaming Laptop',
      price: 999.99,
      originalPrice: 1199.99,
      image: 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500',
      category: 'Electronics',
      description: 'High-performance laptop for work and gaming with RTX graphics',
      brand: 'GameMaster',
      tags: ['laptop', 'gaming', 'rtx', 'high-performance', 'work'],
      color: 'Black',
      rating: 4.8,
      discount: 200
    },
    {
      id: 4,
      name: 'Smartphone Pro',
      price: 699.99,
      originalPrice: 799.99,
      image: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500',
      category: 'Electronics',
      description: 'Latest smartphone with amazing camera and 5G connectivity',
      brand: 'PhoneTech',
      tags: ['smartphone', 'camera', '5g', 'photography', 'mobile'],
      color: 'Blue',
      rating: 4.6,
      discount: 100
    },
    {
      id: 5,
      name: 'Portable Bluetooth Speaker',
      price: 79.99,
      originalPrice: 99.99,
      image: 'https://images.unsplash.com/photo-1545454675-3531b543be5d?w=500',
      category: 'Electronics',
      description: 'Portable bluetooth speaker with great sound and long battery life',
      brand: 'SoundWave',
      tags: ['speaker', 'bluetooth', 'portable', 'bass', 'waterproof'],
      color: 'Red',
      rating: 4.3,
      discount: 20
    },
    {
      id: 6,
      name: 'RGB Gaming Mouse',
      price: 49.99,
      originalPrice: 69.99,
      image: 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500',
      category: 'Electronics',
      description: 'Professional gaming mouse with RGB lighting and precision sensor',
      brand: 'GamerGear',
      tags: ['mouse', 'gaming', 'rgb', 'precision', 'esports'],
      color: 'Black',
      rating: 4.4,
      discount: 20
    },
    {
      id: 7,
      name: 'Mechanical Gaming Keyboard',
      price: 129.99,
      originalPrice: 159.99,
      image: 'https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=500',
      category: 'Electronics',
      description: 'Mechanical keyboard for gaming and typing with RGB backlight',
      brand: 'KeyMaster',
      tags: ['keyboard', 'mechanical', 'gaming', 'rgb', 'typing'],
      color: 'Black',
      rating: 4.7,
      discount: 30
    },
    {
      id: 8,
      name: 'iPad Tablet',
      price: 399.99,
      originalPrice: 449.99,
      image: 'https://images.unsplash.com/photo-1561154464-82e9adf32764?w=500',
      category: 'Electronics',
      description: 'Lightweight tablet for work and entertainment with stylus support',
      brand: 'TabletPro',
      tags: ['tablet', 'stylus', 'drawing', 'work', 'entertainment'],
      color: 'White',
      rating: 4.5,
      discount: 50
    }
  ];

  const categories = ['All', 'Electronics'];

  // Enhanced filter products based on search and category
  const filteredProducts = (() => {
    // If we have backend results from chatbot search, use those
    if (chatbotSearch && backendResults.length > 0) {
      return backendResults.map(convertBackendProduct);
    }

    // Otherwise, use local filtering
    return allProducts.filter(product => {
      const searchLower = searchQuery.toLowerCase();
      const matchesSearch = searchQuery === '' || (
        product.name.toLowerCase().includes(searchLower) ||
        (product.description && product.description.toLowerCase().includes(searchLower)) ||
        product.category.toLowerCase().includes(searchLower) ||
        (product.brand && product.brand.toLowerCase().includes(searchLower)) ||
        (product.color && product.color.toLowerCase().includes(searchLower)) ||
        (product.tags && product.tags.some(tag => tag.toLowerCase().includes(searchLower)))
      );
      const matchesCategory = selectedCategory === 'All' || product.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  })();

  return (
    <div className="products-container">
      <h1 className="products-title">
        Our Products
      </h1>

      {/* Enhanced Search and Filter Section */}
      <div className="search-filter-section">
        <div className="search-filter-wrapper">
          {/* Search Input with Icon and Suggestions */}
          <div className="search-input-container">
            <div className="search-input-wrapper">
              <input
                type="text"
                placeholder="Search for Products"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => setShowSuggestions(true)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
                className="search-input"
              />

              <FontAwesomeIcon 
                icon={faSearch} 
                className="search-icon"
              />

              {/* Search Suggestions Dropdown */}
              {showSuggestions && filteredSuggestions.length > 0 && (
                <div className="search-suggestions">
                  {filteredSuggestions.slice(0, 5).map((suggestion, index) => (
                    <div
                      key={index}
                      className="search-suggestion-item"
                      onMouseDown={() => {
                        setSearchQuery(suggestion);
                        setShowSuggestions(false);
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{ color: '#6c757d', fontSize: '14px' }}>🔍</span>
                        <span style={{ fontSize: '14px', color: '#495057' }}>{suggestion}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Category Dropdown */}
          <div style={{ position: 'relative', minWidth: '200px' }}>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              style={{
                width: '100%',
                padding: '15px 40px 15px 20px',
                border: '2px solid #e9ecef',
                borderRadius: '25px',
                fontSize: '16px',
                backgroundColor: 'white',
                outline: 'none',
                appearance: 'none',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#fed700';
                e.target.style.boxShadow = '0 0 0 3px rgba(254, 215, 0, 0.1)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#e9ecef';
                e.target.style.boxShadow = 'none';
              }}
            >
              {categories.map(category => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
            <div style={{
              position: 'absolute',
              right: '15px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: '#6c757d',
              fontSize: '14px',
              pointerEvents: 'none'
            }}>
              ▼
            </div>
          </div>

          {/* Search Button */}
          <button
            style={{
              backgroundColor: '#fed700',
              color: '#2c3e50',
              border: 'none',
              padding: '15px 30px',
              borderRadius: '25px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              minWidth: '120px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = '#e6c200';
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = '#fed700';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
            }}
          >
            <FontAwesomeIcon icon={faSearch} /> Search
          </button>
        </div>

        {/* Popular Search Tags */}
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '10px',
          marginTop: '15px',
          alignItems: 'center'
        }}>
          <span style={{
            fontSize: '14px',
            color: '#6c757d',
            fontWeight: '500',
            marginRight: '10px'
          }}>
            Popular:
          </span>
          {['gaming', 'wireless', 'rgb', 'bluetooth', 'smartphone'].map((tag) => (
            <button
              key={tag}
              onClick={() => setSearchQuery(tag)}
              style={{
                backgroundColor: searchQuery.toLowerCase().includes(tag) ? '#fed700' : '#f8f9fa',
                color: searchQuery.toLowerCase().includes(tag) ? '#2c3e50' : '#6c757d',
                border: '1px solid #e9ecef',
                padding: '6px 12px',
                borderRadius: '15px',
                fontSize: '12px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                fontWeight: '500'
              }}
              onMouseOver={(e) => {
                if (!searchQuery.toLowerCase().includes(tag)) {
                  e.currentTarget.style.backgroundColor = '#e9ecef';
                  e.currentTarget.style.color = '#495057';
                }
              }}
              onMouseOut={(e) => {
                if (!searchQuery.toLowerCase().includes(tag)) {
                  e.currentTarget.style.backgroundColor = '#f8f9fa';
                  e.currentTarget.style.color = '#6c757d';
                }
              }}
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      {/* Chatbot Search Context */}
      {chatbotSearch && (
        <div style={{
          backgroundColor: '#f0f8ff',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '1px solid #bee5eb'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <span style={{ fontSize: '16px' }}>🤖</span>
            <h3 style={{ margin: 0, color: '#0c5460', fontSize: '16px', fontWeight: '600' }}>
              Chatbot Search Results
            </h3>
          </div>
          <p style={{ margin: '0 0 8px 0', color: '#0c5460', fontSize: '14px' }}>
            Showing results for: "{chatbotSearch.query}"
          </p>
          {(chatbotSearch.category || chatbotSearch.brand || chatbotSearch.minPrice || chatbotSearch.maxPrice) && (
            <div style={{ fontSize: '12px', color: '#6c757d' }}>
              Filters: 
              {chatbotSearch.category && ` Category: ${chatbotSearch.category}`}
              {chatbotSearch.brand && ` | Brand: ${chatbotSearch.brand}`}
              {chatbotSearch.minPrice && ` | Min Price: ${chatbotSearch.minPrice.toLocaleString()} VND`}
              {chatbotSearch.maxPrice && ` | Max Price: ${chatbotSearch.maxPrice.toLocaleString()} VND`}
            </div>
          )}
          {isLoadingBackend && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px' }}>
              <FontAwesomeIcon icon={faSpinner} spin />
              <span style={{ fontSize: '14px', color: '#6c757d' }}>Loading search results...</span>
            </div>
          )}
          {backendError && (
            <div style={{ color: '#dc3545', fontSize: '14px', marginTop: '8px' }}>
              {backendError}
            </div>
          )}
        </div>
      )}

      {/* Search Results Summary */}
      {(searchQuery || selectedCategory !== 'All') && (
        <div style={{
          backgroundColor: '#e8f4fd',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '1px solid #bee5eb'
        }}>
          <p style={{ margin: 0, color: '#0c5460', fontSize: '14px' }}>
            {filteredProducts.length} product{filteredProducts.length !== 1 ? 's' : ''} found
            {searchQuery && ` for "${searchQuery}"`}
            {selectedCategory !== 'All' && ` in ${selectedCategory}`}
          </p>
        </div>
      )}

      {/* Products Grid */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-4">All Products</h2>
      </div>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
        gap: '2rem'
      }}>
        {filteredProducts.length > 0 ? (
          filteredProducts.map((product: Product) => (
            <SimpleProductCard
              key={product.id}
              product={product as any}
              onAddToCart={(product) => addToCart(product as any)}
              onAddToWishlist={(product) => addToWishlist(product as any)}
              isInWishlist={isInWishlist}
            />
          ))
        ) : (
          <div style={{
            gridColumn: '1 / -1',
            textAlign: 'center',
            padding: '60px 20px',
            color: '#666'
          }}>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '10px' }}>No products found</h3>
            <p>Try adjusting your search or filter criteria</p>
          </div>
        )}
      </div>

      {/* Recommendations Section */}
      <div style={{ marginTop: '50px' }}></div>
      <Recommendations 
        limit={3} 
        title="Recommended for You" 
        className="mb-8"
      />

    </div>
    
  );
};

export default Products;
