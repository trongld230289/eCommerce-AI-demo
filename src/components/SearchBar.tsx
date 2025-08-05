import React, { useState, useRef, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch, faTimes } from '@fortawesome/free-solid-svg-icons';
import './SearchBar.css';

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
    <div ref={searchRef} className="searchbar-container">
      {/* Main Search Container */}
      <div className={`searchbar-main ${isInputFocused ? 'focused' : ''}`}>
        {/* Search Input */}
        <div className="searchbar-input-container">
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
            className="searchbar-input"
          />
          {searchQuery && (
            <button
              onClick={clearSearch}
              className="searchbar-clear-button"
            >
              <FontAwesomeIcon icon={faTimes} />
            </button>
          )}
        </div>

        {/* Category Dropdown */}
        <div className="searchbar-category-container">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="searchbar-category-select"
          >
            {categories.map(category => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
          <div className="searchbar-category-arrow">
            ▼
          </div>
        </div>

        {/* Search Button */}
        <button
          onClick={handleSearch}
          className="searchbar-search-button"
        >
          <FontAwesomeIcon icon={faSearch} style={{ color: '#2c3e50' }} />
        </button>
      </div>

      {/* Search Suggestions Dropdown */}
      {showSuggestions && filteredSuggestions.length > 0 && (
        <div className="searchbar-suggestions">
          {/* Search Results Header */}
          <div className="searchbar-results-header">
            <FontAwesomeIcon icon={faSearch} style={{ marginRight: '8px', color: '#6c757d' }} />
            Search Results for "{searchQuery}"
          </div>

          {/* Suggestions List */}
          {filteredSuggestions.map((suggestion, index) => (
            <div
              key={suggestion.id}
              onClick={() => handleSuggestionClick(suggestion)}
              className="searchbar-suggestion-item"
            >
              {/* Product Image */}
              <img
                src={suggestion.image}
                alt={suggestion.name}
                className="searchbar-suggestion-image"
              />
              
              {/* Product Info */}
              <div className="searchbar-suggestion-info">
                <div className="searchbar-suggestion-name">
                  {suggestion.name}
                </div>
                <div className="searchbar-suggestion-category">
                  in {suggestion.category}
                </div>
                <div className="searchbar-suggestion-price">
                  ${suggestion.price}
                </div>
              </div>

              {/* Arrow Icon */}
              <div className="searchbar-suggestion-arrow">
                →
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Popular Search Tags */}
      {showSuggestions && searchQuery.length === 0 && (
        <div className="searchbar-popular-container">
          <div className="searchbar-popular-content">
            <div className="searchbar-popular-title">
              Popular Searches
            </div>
            <div className="searchbar-popular-tags">
              {['iPhone', 'MacBook', 'AirPods', 'iPad', 'Gaming', 'Camera'].map((tag) => (
                <button
                  key={tag}
                  onClick={() => {
                    setSearchQuery(tag);
                    setShowSuggestions(false);
                  }}
                  className="searchbar-popular-tag"
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
