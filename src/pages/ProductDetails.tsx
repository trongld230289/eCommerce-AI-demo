import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faShoppingCart, 
  faHeart, 
  faCompressArrowsAlt,
  faStar,
  faStarHalfAlt,
  faPlus,
  faMinus,
  faCheck,
  faShareAlt
} from '@fortawesome/free-solid-svg-icons';
import { useShop } from '../contexts/ShopContext';
import { useToast } from '../contexts/ToastContext';
import SimpleProductCard from '../components/SimpleProductCard';
import Recommendations from '../components/Recommendations';
import type { Product } from '../contexts/ShopContext';
import './ProductDetails.css';

// Sample products data - in a real app this would come from an API or context
const sampleProducts: Product[] = [
  {
    id: 1,
    name: 'Wireless Headphones',
    price: 99.99,
    originalPrice: 129.99,
    image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500',
    category: 'Electronics',
    description: 'High-quality wireless headphones with noise cancellation',
    brand: 'TechPro',
    rating: 4.5,
    isNew: false,
    discount: 30
  },
  {
    id: 2,
    name: 'Smart Watch',
    price: 199.99,
    image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500',
    category: 'Electronics',
    description: 'Advanced smartwatch with fitness tracking',
    brand: 'FitTech',
    rating: 4.3,
    isNew: true
  },
  {
    id: 3,
    name: 'Laptop Backpack',
    price: 49.99,
    image: 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500',
    category: 'Accessories',
    description: 'Durable laptop backpack with multiple compartments',
    brand: 'TravelGear',
    rating: 4.0
  },
  {
    id: 4,
    name: 'Coffee Maker',
    price: 79.99,
    image: 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=500',
    category: 'Home',
    description: 'Automatic coffee maker with programmable timer',
    brand: 'BrewMaster',
    rating: 4.2
  },
  {
    id: 5,
    name: 'Running Shoes',
    price: 89.99,
    image: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500',
    category: 'Sports',
    description: 'Comfortable running shoes with advanced cushioning',
    brand: 'SportMax',
    rating: 4.4
  }
];

const ProductDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { addToCart, addToWishlist, isInWishlist } = useShop();
  const { showSuccess, showWishlist } = useToast();
  
  const [product, setProduct] = useState<Product | null>(null);
  const [selectedImage, setSelectedImage] = useState(0);
  const [quantity, setQuantity] = useState(1);
  const [selectedColor, setSelectedColor] = useState('');
  const [activeTab, setActiveTab] = useState('description');
  const [relatedProducts, setRelatedProducts] = useState<Product[]>([]);

  // Mock additional product data that would come from API
  const productDetails = {
    images: [
      'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500',
      'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=500',
      'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500',
      'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=500'
    ],
    colors: ['Black', 'White', 'Silver', 'Rose Gold'],
    features: [
      '4.5 inch HD Touch Screen (1280 x 720)',
      'Android 4.4 KitKat OS',
      '1.4 GHz Quad Core™ Processor',
      '20 MP Electro and 28 megapixel CMOS rear camera'
    ],
    description: `Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.`,
    specifications: {
      'Brand': 'TechPro',
      'Model': 'TP-2024',
      'Weight': '1.2 kg',
      'Dimensions': '15 x 10 x 3 cm',
      'Warranty': '2 years',
      'Color Options': 'Multiple'
    },
    reviews: [
      {
        id: 1,
        name: 'John Doe',
        rating: 5,
        comment: 'Excellent product! Very satisfied with the quality.',
        date: '2024-01-15'
      },
      {
        id: 2,
        name: 'Jane Smith',
        rating: 4,
        comment: 'Good value for money. Fast delivery.',
        date: '2024-01-10'
      },
      {
        id: 3,
        name: 'Mike Johnson',
        rating: 5,
        comment: 'Outstanding quality and great customer service.',
        date: '2024-01-05'
      }
    ],
    stock: 26,
    sku: 'FW511948218'
  };

  useEffect(() => {
    if (id) {
      // Find product by ID
      const foundProduct = sampleProducts.find((p: Product) => p.id === parseInt(id));
      if (foundProduct) {
        setProduct(foundProduct);
        setSelectedColor(productDetails.colors[0]);
        
        // Get related products from same category
        const related = sampleProducts
          .filter((p: Product) => p.category === foundProduct.category && p.id !== foundProduct.id)
          .slice(0, 4);
        setRelatedProducts(related);
      } else {
        navigate('/products');
      }
    }
  }, [id, navigate, productDetails.colors]);

  if (!product) {
    return <div className="product-details-loading">Loading...</div>;
  }

  const handleAddToCart = () => {
    for (let i = 0; i < quantity; i++) {
      addToCart(product);
    }
    showSuccess(`${quantity} ${product.name}${quantity > 1 ? 's' : ''} added to cart!`);
  };

  const handleAddToWishlist = () => {
    addToWishlist(product);
    showWishlist(`${product.name} added to wishlist!`);
  };

  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < fullStars; i++) {
      stars.push(<FontAwesomeIcon key={i} icon={faStar} className="star-filled" />);
    }

    if (hasHalfStar) {
      stars.push(<FontAwesomeIcon key="half" icon={faStarHalfAlt} className="star-filled" />);
    }

    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<FontAwesomeIcon key={`empty-${i}`} icon={faStar} className="star-empty" />);
    }

    return stars;
  };

  const averageRating = productDetails.reviews.reduce((acc, review) => acc + review.rating, 0) / productDetails.reviews.length;

  return (
    <div className="product-details">
      {/* Breadcrumb */}
      <div className="breadcrumb">
        <Link to="/">Home</Link>
        <span> / </span>
        <Link to="/products">Products</Link>
        <span> / </span>
        <span>{product.category}</span>
        <span> / </span>
        <span>{product.name}</span>
      </div>

      {/* Main Product Section */}
      <div className="product-main">
        {/* Product Images */}
        <div className="product-images">
          <div className="main-image">
            <img 
              src={productDetails.images[selectedImage]} 
              alt={product.name}
              className="main-product-image"
            />
          </div>
          <div className="image-thumbnails">
            {productDetails.images.map((image, index) => (
              <img
                key={index}
                src={image}
                alt={`${product.name} ${index + 1}`}
                className={`thumbnail ${selectedImage === index ? 'active' : ''}`}
                onClick={() => setSelectedImage(index)}
              />
            ))}
          </div>
        </div>

        {/* Product Info */}
        <div className="product-info">
          <div className="product-category">{product.category}</div>
          <h1 className="product-title">{product.name}</h1>
          
          {/* Rating */}
          <div className="product-rating">
            <div className="stars">
              {renderStars(averageRating)}
            </div>
            <span className="rating-text">
              ({productDetails.reviews.length} customer reviews)
            </span>
          </div>

          {/* Availability */}
          <div className="product-availability">
            <FontAwesomeIcon icon={faCheck} className="check-icon" />
            <span>Availability: {productDetails.stock} in stock</span>
          </div>

          {/* Features */}
          <div className="product-features">
            {productDetails.features.map((feature, index) => (
              <div key={index} className="feature-item">
                • {feature}
              </div>
            ))}
          </div>

          {/* Description */}
          <div className="product-short-description">
            {productDetails.description.split('\n')[0]}
          </div>

          {/* SKU */}
          <div className="product-sku">
            <strong>SKU:</strong> {productDetails.sku}
          </div>

          {/* Price */}
          <div className="product-price">
            <span className="current-price">${product.price}</span>
            {product.originalPrice && (
              <span className="original-price">${product.originalPrice}</span>
            )}
          </div>

          {/* Color Selection */}
          <div className="product-options">
            <div className="color-selection">
              <label>Color:</label>
              <div className="color-options">
                {productDetails.colors.map((color) => (
                  <button
                    key={color}
                    className={`color-option ${selectedColor === color ? 'selected' : ''}`}
                    onClick={() => setSelectedColor(color)}
                    title={color}
                  >
                    {color}
                  </button>
                ))}
              </div>
            </div>

            {/* Quantity Selection */}
            <div className="quantity-selection">
              <label>Quantity:</label>
              <div className="quantity-controls">
                <button 
                  className="quantity-btn"
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  disabled={quantity <= 1}
                >
                  <FontAwesomeIcon icon={faMinus} />
                </button>
                <span className="quantity-display">{quantity}</span>
                <button 
                  className="quantity-btn"
                  onClick={() => setQuantity(Math.min(productDetails.stock, quantity + 1))}
                  disabled={quantity >= productDetails.stock}
                >
                  <FontAwesomeIcon icon={faPlus} />
                </button>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="product-actions">
            <button className="add-to-cart-btn" onClick={handleAddToCart}>
              <FontAwesomeIcon icon={faShoppingCart} />
              Add to Cart
            </button>
            <button 
              className={`wishlist-btn ${isInWishlist(product.id) ? 'active' : ''}`}
              onClick={handleAddToWishlist}
            >
              <FontAwesomeIcon icon={faHeart} />
              Wishlist
            </button>
            <button className="compare-btn">
              <FontAwesomeIcon icon={faCompressArrowsAlt} />
              Compare
            </button>
            <button className="share-btn">
              <FontAwesomeIcon icon={faShareAlt} />
              Share
            </button>
          </div>
        </div>
      </div>

      {/* Product Details Tabs */}
      <div className="product-tabs">
        <div className="tab-headers">
          <button 
            className={`tab-header ${activeTab === 'description' ? 'active' : ''}`}
            onClick={() => setActiveTab('description')}
          >
            Description
          </button>
          <button 
            className={`tab-header ${activeTab === 'specifications' ? 'active' : ''}`}
            onClick={() => setActiveTab('specifications')}
          >
            Specifications
          </button>
          <button 
            className={`tab-header ${activeTab === 'reviews' ? 'active' : ''}`}
            onClick={() => setActiveTab('reviews')}
          >
            Reviews ({productDetails.reviews.length})
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'description' && (
            <div className="description-content">
              <h3>Product Description</h3>
              {productDetails.description.split('\n').map((paragraph, index) => (
                <p key={index}>{paragraph}</p>
              ))}
            </div>
          )}

          {activeTab === 'specifications' && (
            <div className="specifications-content">
              <h3>Product Specifications</h3>
              <table className="specs-table">
                <tbody>
                  {Object.entries(productDetails.specifications).map(([key, value]) => (
                    <tr key={key}>
                      <td className="spec-label">{key}</td>
                      <td className="spec-value">{value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'reviews' && (
            <div className="reviews-content">
              <h3>Customer Reviews</h3>
              <div className="reviews-summary">
                <div className="average-rating">
                  <div className="rating-number">{averageRating.toFixed(1)}</div>
                  <div className="stars">
                    {renderStars(averageRating)}
                  </div>
                  <div className="total-reviews">Based on {productDetails.reviews.length} reviews</div>
                </div>
              </div>
              
              <div className="reviews-list">
                {productDetails.reviews.map((review) => (
                  <div key={review.id} className="review-item">
                    <div className="review-header">
                      <div className="reviewer-name">{review.name}</div>
                      <div className="review-rating">
                        {renderStars(review.rating)}
                      </div>
                      <div className="review-date">{new Date(review.date).toLocaleDateString()}</div>
                    </div>
                    <div className="review-comment">{review.comment}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Related Products */}
      {relatedProducts.length > 0 && (
        <div className="related-products">
          <h2>Related Products</h2>
          <div className="related-products-grid">
            {relatedProducts.map((relatedProduct) => (
              <SimpleProductCard
                key={relatedProduct.id}
                product={relatedProduct}
                onAddToCart={addToCart}
                onAddToWishlist={addToWishlist}
                isInWishlist={isInWishlist}
              />
            ))}
          </div>
        </div>
      )}

      {/* You Might Also Like Section */}
      <div className="recommendations-section" style={{ marginTop: '3rem', padding: '2rem 0', backgroundColor: '#f8fafc' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 1rem' }}>
          <Recommendations 
            limit={4} 
            title="You Might Also Like" 
            className=""
          />
        </div>
      </div>
    </div>
  );
};

export default ProductDetails;
