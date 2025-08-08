import React, { useState, useRef, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch, faTimes } from '@fortawesome/free-solid-svg-icons';

interface SearchSuggestion {
  id: number;
  name: string;
  category: string;
  image: string;
  price: number;
}

interface SearchBarProps {
  onSearch?: (query: string, category: string) => void;
  onProductSelect?: (product: SearchSuggestion) => void;
  placeholder?: string;
  suggestions?: SearchSuggestion[];
}

const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  onProductSelect,
  placeholder = "Search for Products",
  suggestions = []
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isInputFocused, setIsInputFocused] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  const categories = [
    'All Categories',
    'Electronics',
    'Smartphones', 
    'Laptops',
    'Headphones',
    'Cameras',
    'Gaming',
    'Audio',
    'Tablets',
    'Smartwatches'
  ];

  // Mock search suggestions - in real app this would come from API
  const mockSuggestions: SearchSuggestion[] = [
    { id: 1, name: 'iPhone 15 Pro', category: 'Smartphones', image: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=100', price: 999 },
    { id: 2, name: 'MacBook Pro M3', category: 'Laptops', image: 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=100', price: 1999 },
    { id: 3, name: 'AirPods Pro', category: 'Headphones', image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=100', price: 249 },
    { id: 4, name: 'iPad Air', category: 'Tablets', image: 'https://images.unsplash.com/photo-1561154464-82e9adf32764?w=100', price: 599 },
    { id: 5, name: 'Canon EOS R5', category: 'Cameras', image: 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=100', price: 3899 }
  ];

  const filteredSuggestions = mockSuggestions.filter(item =>
    searchQuery.length > 2 && 
    item.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSearch = () => {
    if (onSearch) {
      onSearch(searchQuery, selectedCategory);
    }
    setShowSuggestions(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleSuggestionClick = (suggestion: SearchSuggestion) => {
    setSearchQuery(suggestion.name);
    setShowSuggestions(false);
    if (onProductSelect) {
      onProductSelect(suggestion);
    }
  };

  const clearSearch = () => {
    setSearchQuery('');
    setShowSuggestions(false);
  };

  // Inline styles
  const styles = {
    searchbarContainer: {
      position: 'relative' as const,
      width: '100%',
      maxWidth: '900px'
    },
    searchbarMain: {
      display: 'flex',
      backgroundColor: 'white',
      borderRadius: '25px',
      boxShadow: isInputFocused ? '0 4px 20px rgba(254, 215, 0, 0.3)' : '0 2px 8px rgba(0,0,0,0.1)',
      overflow: 'hidden',
      border: isInputFocused ? '2px solid #fed700' : '2px solid transparent',
      transition: 'all 0.3s ease'
    },
    searchbarInputContainer: {
      flex: 1,
      position: 'relative' as const,
      display: 'flex',
      alignItems: 'center'
    },
    searchbarInput: {
      width: '100%',
      padding: '8px 20px',
      border: 'none',
      outline: 'none',
      fontSize: '14px',
      fontFamily: "'Open Sans', Arial, sans-serif",
      backgroundColor: 'transparent',
      boxShadow: 'none'
    },
    searchbarClearButton: {
      position: 'absolute' as const,
      right: '15px',
      background: 'none',
      border: 'none',
      cursor: 'pointer',
      color: '#6c757d',
      fontSize: '14px',
      padding: '5px'
    },
    searchbarCategoryContainer: {
      borderLeft: '1px solid #e9ecef',
      position: 'relative' as const
    },
    searchbarCategorySelect: {
      padding: '12px 40px 12px 20px',
      border: 'none',
      outline: 'none',
      fontSize: '14px',
      fontFamily: "'Open Sans', Arial, sans-serif",
      backgroundColor: 'transparent',
      cursor: 'pointer',
      appearance: 'none' as const,
      minWidth: '160px',
      color: '#495057',
      boxShadow: 'none'
    },
    searchbarCategoryArrow: {
      position: 'absolute' as const,
      right: '15px',
      top: '50%',
      transform: 'translateY(-50%)',
      pointerEvents: 'none' as const,
      color: '#6c757d'
    },
    searchbarSearchButton: {
      backgroundColor: '#fed700',
      border: 'none',
      padding: '12px 25px',
      cursor: 'pointer',
      fontSize: '16px',
      transition: 'all 0.3s ease',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minWidth: '70px'
    },
    searchbarSuggestions: {
      position: 'absolute' as const,
      top: '100%',
      left: 0,
      right: 0,
      backgroundColor: 'white',
      borderRadius: '12px',
      boxShadow: '0 8px 30px rgba(0,0,0,0.15)',
      zIndex: 1000,
      marginTop: '8px',
      maxHeight: '400px',
      overflowY: 'auto' as const,
      border: '1px solid #e9ecef'
    },
    searchbarResultsHeader: {
      padding: '15px 20px',
      borderBottom: '1px solid #f1f3f4',
      fontSize: '14px',
      fontWeight: 600,
      color: '#495057',
      backgroundColor: '#f8f9fa'
    },
    searchbarSuggestionItem: {
      padding: '15px 20px',
      cursor: 'pointer',
      borderBottom: '1px solid #f1f3f4',
      transition: 'background-color 0.2s ease',
      display: 'flex',
      alignItems: 'center',
      gap: '15px'
    },
    searchbarSuggestionImage: {
      width: '50px',
      height: '50px',
      objectFit: 'cover' as const,
      borderRadius: '8px',
      border: '1px solid #e9ecef'
    },
    searchbarSuggestionInfo: {
      flex: 1
    },
    searchbarSuggestionName: {
      fontWeight: 500,
      color: '#2c3e50',
      fontSize: '14px',
      marginBottom: '4px'
    },
    searchbarSuggestionCategory: {
      fontSize: '12px',
      color: '#6c757d',
      marginBottom: '4px'
    },
    searchbarSuggestionPrice: {
      fontSize: '14px',
      color: '#28a745',
      fontWeight: 600
    },
    searchbarSuggestionArrow: {
      color: '#6c757d',
      fontSize: '12px'
    },
    searchbarPopularContainer: {
      position: 'absolute' as const,
      top: '100%',
      left: 0,
      right: 0,
      backgroundColor: 'white',
      borderRadius: '12px',
      boxShadow: '0 8px 30px rgba(0,0,0,0.15)',
      zIndex: 1000,
      marginTop: '8px',
      border: '1px solid #e9ecef'
    },
    searchbarPopularContent: {
      padding: '20px'
    },
    searchbarPopularTitle: {
      fontSize: '14px',
      fontWeight: 600,
      color: '#495057',
      marginBottom: '15px'
    },
    searchbarPopularTags: {
      display: 'flex',
      flexWrap: 'wrap' as const,
      gap: '8px'
    },
    searchbarPopularTag: {
      backgroundColor: '#f8f9fa',
      border: '1px solid #e9ecef',
      padding: '8px 15px',
      borderRadius: '20px',
      fontSize: '12px',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      color: '#495057'
    }
  };

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
        setIsInputFocused(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={searchRef} style={styles.searchbarContainer}>
      {/* Main Search Container */}
      <div style={styles.searchbarMain}>
        {/* Search Input */}
        <div style={styles.searchbarInputContainer}>
          <input
            type="text"
            placeholder={placeholder}
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setShowSuggestions(e.target.value.length > 0);
            }}
            onFocus={() => {
              setIsInputFocused(true);
              setShowSuggestions(searchQuery.length > 0);
            }}
            onKeyPress={handleKeyPress}
            style={styles.searchbarInput}
          />
          {searchQuery && (
            <button
              onClick={clearSearch}
              style={styles.searchbarClearButton}
            >
              <FontAwesomeIcon icon={faTimes} />
            </button>
          )}
        </div>

        {/* Category Dropdown */}
        <div style={styles.searchbarCategoryContainer}>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            style={styles.searchbarCategorySelect}
          >
            {categories.map(category => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
          <div style={styles.searchbarCategoryArrow}>
            ▼
          </div>
        </div>

        {/* Search Button */}
        <button
          onClick={handleSearch}
          style={styles.searchbarSearchButton}
          onMouseOver={(e) => {
            e.currentTarget.style.backgroundColor = '#e6c200';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.backgroundColor = '#fed700';
          }}
        >
          <FontAwesomeIcon icon={faSearch} style={{ color: '#2c3e50' }} />
        </button>
      </div>

      {/* Search Suggestions Dropdown */}
      {showSuggestions && filteredSuggestions.length > 0 && (
        <div style={styles.searchbarSuggestions}>
          {/* Search Results Header */}
          <div style={styles.searchbarResultsHeader}>
            <FontAwesomeIcon icon={faSearch} style={{ marginRight: '8px', color: '#6c757d' }} />
            Search Results for "{searchQuery}"
          </div>

          {/* Suggestions List */}
          {filteredSuggestions.map((suggestion, index) => (
            <div
              key={suggestion.id}
              onClick={() => handleSuggestionClick(suggestion)}
              style={{
                ...styles.searchbarSuggestionItem,
                borderBottom: index === filteredSuggestions.length - 1 ? 'none' : '1px solid #f1f3f4'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = '#f8f9fa';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              {/* Product Image */}
              <img
                src={suggestion.image}
                alt={suggestion.name}
                style={styles.searchbarSuggestionImage}
              />
              
              {/* Product Info */}
              <div style={styles.searchbarSuggestionInfo}>
                <div style={styles.searchbarSuggestionName}>
                  {suggestion.name}
                </div>
                <div style={styles.searchbarSuggestionCategory}>
                  in {suggestion.category}
                </div>
                <div style={styles.searchbarSuggestionPrice}>
                  ${suggestion.price}
                </div>
              </div>

              {/* Arrow Icon */}
              <div style={styles.searchbarSuggestionArrow}>
                →
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Popular Search Tags */}
      {showSuggestions && searchQuery.length === 0 && (
        <div style={styles.searchbarPopularContainer}>
          <div style={styles.searchbarPopularContent}>
            <div style={styles.searchbarPopularTitle}>
              Popular Searches
            </div>
            <div style={styles.searchbarPopularTags}>
              {['iPhone', 'MacBook', 'AirPods', 'iPad', 'Gaming', 'Camera'].map((tag) => (
                <button
                  key={tag}
                  onClick={() => {
                    setSearchQuery(tag);
                    setShowSuggestions(false);
                  }}
                  style={styles.searchbarPopularTag}
                  onMouseOver={(e) => {
                    e.currentTarget.style.backgroundColor = '#fed700';
                    e.currentTarget.style.color = '#2c3e50';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.backgroundColor = '#f8f9fa';
                    e.currentTarget.style.color = '#495057';
                  }}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchBar;
