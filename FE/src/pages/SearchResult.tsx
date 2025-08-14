import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SimpleProductCard from '../components/SimpleProductCard';
import { Product, useShop } from '../contexts/ShopContext';
import { useToast } from '../contexts/ToastContext';

const SearchResult: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { addToCart } = useShop();
  const { showSuccess } = useToast();

  // Toast handler for cart actions
  const handleAddToCart = (product: Product) => {
    addToCart(product);
    showSuccess(`${product.name} added to cart!`, 'Check your cart to proceed to checkout.');
  };

  useEffect(() => {
    console.log('🔍 SearchResult page loaded');
    
    // Get products from sessionStorage (from chatbot)
    const storedProducts = sessionStorage.getItem('chatbotSearchResults');
    const storedQuery = sessionStorage.getItem('chatbotSearchQuery');
    
    console.log('📦 Stored products:', storedProducts);
    console.log('🔎 Stored query:', storedQuery);
    
    if (storedProducts && storedQuery) {
      try {
        const parsedProducts = JSON.parse(storedProducts);
        setProducts(parsedProducts);
  // setSearchQuery(storedQuery); // removed, not needed
        console.log('✅ Successfully loaded chatbot search results:', parsedProducts.length, 'products');
      } catch (error) {
        console.error('❌ Error parsing stored products:', error);
        // Fallback: redirect to main products page
        navigate('/products');
      }
    } else {
      console.warn('⚠️ No chatbot search results found, redirecting to products page');
      // No stored results, redirect to main products page
      navigate('/products');
    }
    
    setLoading(false);
  }, [navigate]);


  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading search results...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa' }}>
      <div style={{ 
        padding: '20px',
        maxWidth: '1430px',
        margin: '0 auto'
      }}>
        <h2 style={{
          fontSize: '1.5rem',
          fontWeight: 600,
          color: '#2c3e50',
          textAlign: 'center',
          marginBottom: '2rem',
          fontFamily: "'Open Sans', Arial, sans-serif"
        }}>
          All Products
        </h2>
        {products.length > 0 ? (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
            gap: '2rem'
          }}>
            {products.map((product) => (
              <SimpleProductCard 
                key={product.id} 
                product={product} 
                onAddToCart={handleAddToCart}
              />
            ))}
          </div>
        ) : (
          <div style={{
            textAlign: 'center',
            padding: '3rem 0'
          }}>
            <div style={{ fontSize: '4rem', marginBottom: '1rem', color: '#9ca3af' }}>🔍</div>
            <h3 style={{ 
              fontSize: '1.25rem', 
              fontWeight: 600, 
              color: '#111827', 
              marginBottom: '0.5rem' 
            }}>
              No products found
            </h3>
            <p style={{ color: '#6b7280' }}>
              Try searching with different keywords or browse our categories.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchResult;
