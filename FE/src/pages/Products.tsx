import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useShop } from '../contexts/ShopContext';
import { useToast } from '../contexts/ToastContext';
import type { Product } from '../contexts/ShopContext';
import SimpleProductCard from '../components/SimpleProductCard';
import Recommendations from '../components/Recommendations';
import { searchService } from '../services/searchService';
import { aiService } from '../services/aiService';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch, faSpinner } from '@fortawesome/free-solid-svg-icons';

const Products: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { addToCart, addToWishlist, isInWishlist } = useShop();
  const { showSuccess, showWishlist, showWarning } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [showSuggestions, setShowSuggestions] = useState(false);
  
  // Add state for loading all products from backend
  const [allProducts, setAllProducts] = useState<Product[]>([]);
  const [isLoadingProducts, setIsLoadingProducts] = useState(false);
  const [productsError, setProductsError] = useState<string | null>(null);
  const [categories, setCategories] = useState<string[]>(['All', 'Electronics']);

  // Initialize from URL parameters and handle AI search
  useEffect(() => {
    const query = searchParams.get('q') || '';
    const category = searchParams.get('category') || 'All';
    const isAiSearch = searchParams.get('ai_search') === 'true';

    setSearchQuery(query);
    setSelectedCategory(category);
    
    // AI search functionality
    const performAISearch = async (searchQuery: string) => {
      setIsLoadingProducts(true);
      setProductsError(null);
      
      try {
        const aiResponse = await aiService.searchProducts({
          messages: [{ role: "user", content: searchQuery }],
          limit: 20
        });
        
        if (aiResponse.status === 'success' && aiResponse.products) {
          const products = aiService.convertToProducts(aiResponse.products);
          setAllProducts(products);
          
          // Show success message with search intent if available
          if (aiResponse.search_intent) {
            const intent = aiResponse.search_intent;
            let intentMessage = `AI Search found ${products.length} results for "${searchQuery}".`;
            
            if (intent.filters.category) {
              intentMessage += ` Filtered by category: ${intent.filters.category}.`;
            }
            if (intent.filters.min_price || intent.filters.max_price) {
              intentMessage += ` Price filters applied.`;
            }
            if (intent.filters.min_rating) {
              intentMessage += ` Minimum rating: ${intent.filters.min_rating} stars.`;
            }
            
            showSuccess(intentMessage);
          } else {
            showSuccess(`AI Search found ${products.length} results for "${searchQuery}".`);
          }
        } else {
          // Fallback to regular search if AI search fails
          await loadTop8Products();
          showWarning(`AI Search couldn't find results for "${searchQuery}". Showing default products.`);
        }
      } catch (error) {
        console.error('AI search error:', error);
        // Fallback to regular search
        await loadTop8Products();
        showWarning(`Search error occurred. Showing default products.`);
      } finally {
        setIsLoadingProducts(false);
      }
    };
    
    // If there's a search query and it's marked as AI search, perform AI search
    if (query && isAiSearch) {
      performAISearch(query);
    }
  }, [searchParams, showSuccess, showWarning]);

  // Load top 8 products from backend on component mount (only when no search is active)
  useEffect(() => {
    loadTop8Products();
  }, []);

  // Load top 8 products from backend
  const loadTop8Products = async () => {
    setIsLoadingProducts(true);
    setProductsError(null);
    
    try {
      // Get all products from backend
      const allBackendProducts = await searchService.getAllProducts();
      
      // Take only the top 8 products
      const top8Products = allBackendProducts.slice(0, 8);
      
      setAllProducts(top8Products);
      
      // Load categories from backend
      try {
        // const backendCategories = await searchService.getCategories();
        // setCategories(backendCategories);
      } catch (categoryError) {
        console.warn('Failed to load categories, using default:', categoryError);
        // setCategories(['All', 'Electronics']);
      }
      
    } catch (error) {
      console.error('Failed to load products from backend:', error);
      setProductsError('Failed to load products from server');
    } finally {
      setIsLoadingProducts(false);
    }
  };

  // Responsive state
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 480);
  const [isTablet, setIsTablet] = useState(window.innerWidth <= 768);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 480);
      setIsTablet(window.innerWidth <= 768);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Inline styles object
  const styles = {
    productsSection: {
      padding: '3rem 0',
      backgroundColor: 'white'
    },
    sectionTitle: {
      fontSize: '1.5rem',
      fontWeight: 600,
      color: '#2c3e50',
      textAlign: 'center' as const,
      marginBottom: '2rem',
      fontFamily: "'Open Sans', Arial, sans-serif"
    },
    productsContainer: {
      padding: isMobile ? '15px' : '20px',
      maxWidth: '1430px',
      margin: '0 auto'
    },
    productsTitle: {
      fontSize: isMobile ? '2rem' : '2.5rem',
      fontWeight: 'bold',
      marginBottom: '30px',
      textAlign: 'center' as const
    },
    searchFilterSection: {
      backgroundColor: '#f8f9fa',
      padding: isMobile ? '20px' : '25px',
      borderRadius: '12px',
      marginBottom: '30px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
    },
    searchFilterWrapper: {
      display: 'flex',
      gap: '15px',
      flexWrap: 'wrap' as const,
      alignItems: 'stretch',
      flexDirection: isTablet ? 'column' as const : 'row' as const
    },
    searchInputContainer: {
      flex: 1,
      minWidth: isTablet ? 'auto' : '300px',
      position: 'relative' as const
    },
    searchInputWrapper: {
      position: 'relative' as const
    },
    searchInput: {
      width: '100%',
      padding: isMobile ? '12px 45px 12px 15px' : '15px 50px 15px 20px',
      border: '2px solid #e9ecef',
      borderRadius: '25px',
      fontSize: isMobile ? '14px' : '16px',
      outline: 'none',
      transition: 'all 0.3s ease',
      boxSizing: 'border-box' as const
    },
    searchIcon: {
      position: 'absolute' as const,
      right: '20px',
      top: '50%',
      transform: 'translateY(-50%)',
      color: '#6c757d',
      pointerEvents: 'none' as const
    },
    searchSuggestions: {
      position: 'absolute' as const,
      top: '100%',
      left: 0,
      right: 0,
      background: 'white',
      border: '1px solid #e9ecef',
      borderRadius: '8px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
      zIndex: 1000,
      maxHeight: '200px',
      overflowY: 'auto' as const
    },
    searchSuggestionItem: {
      padding: '12px 20px',
      cursor: 'pointer',
      transition: 'background-color 0.2s',
      borderBottom: '1px solid #f8f9fa'
    },
    categoryDropdownContainer: {
      position: 'relative' as const,
      minWidth: isTablet ? 'auto' : '200px'
    },
    categoryDropdown: {
      width: '100%',
      padding: isMobile ? '12px 35px 12px 15px' : '15px 40px 15px 20px',
      border: '2px solid #e9ecef',
      borderRadius: '25px',
      fontSize: isMobile ? '14px' : '16px',
      backgroundColor: 'white',
      outline: 'none',
      appearance: 'none' as const,
      cursor: 'pointer',
      transition: 'all 0.3s ease'
    },
    dropdownArrow: {
      position: 'absolute' as const,
      right: '15px',
      top: '50%',
      transform: 'translateY(-50%)',
      color: '#6c757d',
      fontSize: '14px',
      pointerEvents: 'none' as const
    },
    resultsSection: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: isTablet ? 'flex-start' : 'center',
      marginBottom: '25px',
      flexWrap: 'wrap' as const,
      gap: '15px',
      flexDirection: isTablet ? 'column' as const : 'row' as const
    },
    resultsInfo: {
      fontSize: '16px',
      color: '#6c757d'
    },
    resultsCount: {
      color: '#fed700',
      fontWeight: 'bold'
    },
    sortDropdown: {
      padding: '10px 15px',
      border: '2px solid #e9ecef',
      borderRadius: '20px',
      fontSize: '14px',
      backgroundColor: 'white',
      outline: 'none',
      cursor: 'pointer',
      transition: 'all 0.3s ease'
    },
    productsGrid: {
      display: 'grid',
      gridTemplateColumns: isMobile ? '1fr' : isTablet ? 'repeat(auto-fill, minmax(250px, 1fr))' : 'repeat(auto-fill, minmax(280px, 1fr))',
      gap: isMobile ? '1rem' : isTablet ? '1.5rem' : '2rem',
      marginBottom: '2rem'
    },
    noProducts: {
      textAlign: 'center' as const,
      padding: '4rem 2rem',
      backgroundColor: 'white',
      borderRadius: '12px',
      border: '2px dashed #e9ecef'
    },
    noProductsIcon: {
      fontSize: '4rem',
      marginBottom: '1rem',
      color: '#6c757d'
    },
    noProductsTitle: {
      fontSize: '1.5rem',
      color: '#495057',
      marginBottom: '1rem',
      fontWeight: 600
    },
    noProductsText: {
      color: '#6c757d',
      marginBottom: '2rem',
      fontSize: '1.1rem'
    },
    clearSearchButton: {
      backgroundColor: '#fed700',
      color: '#212529',
      border: 'none',
      padding: '12px 24px',
      borderRadius: '25px',
      fontSize: '16px',
      fontWeight: 600,
      cursor: 'pointer',
      transition: 'all 0.3s ease'
    }
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

  // Toast handlers for cart and wishlist actions
  const handleAddToCart = (product: Product) => {
    addToCart(product);
    showSuccess(`${product.name} added to cart!`, 'Check your cart to proceed to checkout.');
  };

  const handleAddToWishlist = (product: Product) => {
    if (isInWishlist(product.id)) {
      showWarning(`Already in wishlist!`, `${product.name} is already in your wishlist.`);
    } else {
      addToWishlist(product);
      showWishlist(`${product.name} added to wishlist!`, 'View your wishlist to see all saved items.');
    }
  };

  // Simple search handler
  const handleSearch = () => {
    // Update URL parameters
    const params = new URLSearchParams();
    if (searchQuery.trim()) params.set('q', searchQuery);
    if (selectedCategory !== 'All') params.set('category', selectedCategory);
    setSearchParams(params);

    // Count results
    const resultCount = filteredProducts.length;
    if (searchQuery.trim()) {
      if (resultCount > 0) {
        showSuccess(`Found ${resultCount} product${resultCount !== 1 ? 's' : ''}!`, `Search results for "${searchQuery}"`);
      } else {
        showWarning('No products found', `Try different keywords for "${searchQuery}"`);
      }
    }
  };

  // Simple filter products based on search and category
  const filteredProducts = allProducts.filter(product => {
    const searchLower = searchQuery.toLowerCase();
    const matchesSearch = searchQuery === '' || (
      product.name.toLowerCase().includes(searchLower) ||
      (product.description && product.description.toLowerCase().includes(searchLower)) ||
      product.category.toLowerCase().includes(searchLower)
    );
    const matchesCategory = selectedCategory === 'All' || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div style={styles.productsContainer}>
      <h1 style={styles.productsTitle}>
        Our Products
      </h1>

      {/* Enhanced Search and Filter Section */}
      <div style={styles.searchFilterSection}>
        <div style={styles.searchFilterWrapper}>
          {/* Search Input with Icon and Suggestions */}
          <div style={styles.searchInputContainer}>
            <div style={styles.searchInputWrapper}>
              <input
                type="text"
                placeholder="Search for Products"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => setShowSuggestions(true)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
                style={styles.searchInput}
              />

              <FontAwesomeIcon
                icon={faSearch}
                style={styles.searchIcon}
              />

              {/* Search Suggestions Dropdown */}
              {showSuggestions && filteredSuggestions.length > 0 && (
                <div style={styles.searchSuggestions}>
                  {filteredSuggestions.slice(0, 5).map((suggestion, index) => (
                    <div
                      key={index}
                      style={styles.searchSuggestionItem}
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
          <div style={styles.categoryDropdownContainer}>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              style={styles.categoryDropdown}
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
            <div style={styles.dropdownArrow}>
              ▼
            </div>
          </div>

          {/* Search Button */}
          <button
            onClick={handleSearch}
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
      <section style={styles.productsSection}>
        <div style={styles.productsContainer}>
          <h2 style={styles.sectionTitle}>
            All Products
          </h2>
          
          {/* Loading State */}
          {isLoadingProducts && (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              padding: '60px 20px',
              color: '#666'
            }}>
              <FontAwesomeIcon icon={faSpinner} spin style={{ fontSize: '2rem', marginBottom: '15px' }} />
              <h3 style={{ fontSize: '1.2rem', marginBottom: '10px' }}>Loading products...</h3>
              <p>Please wait while we fetch the latest products</p>
            </div>
          )}
          
          {/* Error State */}
          {productsError && !isLoadingProducts && (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              padding: '60px 20px',
              color: '#dc3545',
              backgroundColor: '#f8d7da',
              borderRadius: '8px',
              border: '1px solid #f5c6cb',
              marginBottom: '20px'
            }}>
              <h3 style={{ fontSize: '1.2rem', marginBottom: '10px' }}>Error loading products</h3>
              <p style={{ marginBottom: '15px' }}>{productsError}</p>
              <button
                onClick={loadTop8Products}
                style={{
                  backgroundColor: '#007bff',
                  color: 'white',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '5px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                Retry
              </button>
            </div>
          )}
          
          {/* Products Grid */}
          {!isLoadingProducts && (
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
                    onAddToCart={handleAddToCart}
                  />
                ))
              ) : (
                <div style={{
                  gridColumn: '1 / -1',
                  textAlign: 'center',
                  padding: '60px 20px',
                  color: '#666'
                }}>
                  <h3 style={{ fontSize: '1.5rem', marginBottom: '10px' }}>
                    {productsError ? 'No products available' : 'No products found'}
                  </h3>
                  <p>
                    {productsError 
                      ? 'Please try again later or contact support' 
                      : 'Try adjusting your search or filter criteria'
                    }
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </section>

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

