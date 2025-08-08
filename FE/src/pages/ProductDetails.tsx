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
  faShareAlt,
  faSpinner
} from '@fortawesome/free-solid-svg-icons';
import { useShop } from '../contexts/ShopContext';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import SimpleProductCard from '../components/SimpleProductCard';
import Recommendations from '../components/Recommendations';
import { apiService } from '../services/apiService';
import { eventTrackingService } from '../services/eventTrackingService';
import type { Product } from '../contexts/ShopContext';

const ProductDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { addToCart, addToWishlist, isInWishlist } = useShop();
  const { currentUser } = useAuth();
  const { showSuccess, showWishlist } = useToast();
  
  // Product state
  const [product, setProduct] = useState<Product | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Add responsive state
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const [isSmallMobile, setIsSmallMobile] = useState(window.innerWidth <= 480);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
      setIsSmallMobile(window.innerWidth <= 480);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Load product data from API
  useEffect(() => {
    const loadProduct = async () => {
      if (!id) {
        setError('Product ID not provided');
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const productData = await apiService.getProductById(parseInt(id));
        setProduct(productData);
        
        // Track product view event
        if (currentUser && productData) {
          eventTrackingService.trackProductView(currentUser.uid, productData.id.toString(), {
            product_name: productData.name,
            product_category: productData.category,
            product_brand: productData.brand,
            product_price: productData.price,
          }).catch(error => {
            console.error('Failed to track product view event:', error);
          });
        }
      } catch (err) {
        console.error('Error loading product:', err);
        setError('Product not found');
      } finally {
        setIsLoading(false);
      }
    };

    loadProduct();
  }, [id, currentUser]);

  // Inline styles object
  const styles = {
    productDetails: {
      maxWidth: '1430px',
      margin: '0 auto',
      padding: isMobile ? '15px' : '20px',
      fontFamily: "'Open Sans', Arial, sans-serif"
    },
    breadcrumb: {
      padding: '10px 0',
      marginBottom: '20px',
      fontSize: isSmallMobile ? '12px' : '14px',
      color: '#6c757d'
    },
    breadcrumbLink: {
      color: '#007bff',
      textDecoration: 'none'
    },
    productDetailsLoading: {
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '50vh',
      fontSize: '18px',
      color: '#6c757d'
    },
    productMain: {
      display: 'grid',
      gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr',
      gap: isMobile ? '30px' : '40px',
      marginBottom: '40px'
    },
    productImages: {
      display: 'flex',
      flexDirection: 'column' as const,
      gap: '15px'
    },
    mainImage: {
      width: '100%',
      aspectRatio: '1',
      overflow: 'hidden',
      borderRadius: '8px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
    },
    mainProductImage: {
      width: '100%',
      height: '100%',
      objectFit: 'cover' as const,
      transition: 'transform 0.3s ease'
    },
    imageThumbnails: {
      display: 'flex',
      gap: '10px',
      overflowX: 'auto' as const,
      padding: '5px 0',
      justifyContent: isMobile ? 'center' : 'flex-start'
    },
    thumbnail: {
      width: '80px',
      height: '80px',
      objectFit: 'cover' as const,
      borderRadius: '6px',
      cursor: 'pointer',
      opacity: 0.7,
      transition: 'all 0.3s ease',
      border: '2px solid transparent'
    },
    thumbnailActive: {
      opacity: 1,
      borderColor: '#fed700',
      boxShadow: '0 0 10px rgba(254, 215, 0, 0.3)'
    },
    productInfo: {
      padding: isMobile ? '0' : '0 20px'
    },
    productCategory: {
      color: '#007bff',
      fontSize: '14px',
      fontWeight: 600,
      marginBottom: '10px',
      textTransform: 'uppercase' as const,
      letterSpacing: '0.5px'
    },
    productTitle: {
      fontSize: isSmallMobile ? '20px' : isMobile ? '24px' : '28px',
      fontWeight: 700,
      color: '#333',
      marginBottom: '15px',
      lineHeight: 1.3
    },
    productRating: {
      display: 'flex',
      alignItems: 'center',
      gap: '10px',
      marginBottom: '15px'
    },
    stars: {
      display: 'flex',
      gap: '2px'
    },
    starFilled: {
      color: '#ffc107',
      fontSize: '16px'
    },
    starEmpty: {
      color: '#e9ecef',
      fontSize: '16px'
    },
    ratingText: {
      color: '#6c757d',
      fontSize: '14px'
    },
    productAvailability: {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      marginBottom: '20px',
      color: '#28a745',
      fontWeight: 600
    },
    checkIcon: {
      color: '#28a745'
    },
    productFeatures: {
      backgroundColor: '#f8f9fa',
      padding: '20px',
      borderRadius: '8px',
      marginBottom: '20px'
    },
    featureItem: {
      marginBottom: '8px',
      color: '#495057',
      fontSize: '14px',
      lineHeight: 1.5
    },
    productShortDescription: {
      color: '#6c757d',
      fontSize: '16px',
      lineHeight: 1.6,
      marginBottom: '20px'
    },
    productSku: {
      fontSize: '14px',
      color: '#6c757d',
      marginBottom: '20px'
    },
    productPrice: {
      marginBottom: '30px'
    },
    currentPrice: {
      fontSize: isSmallMobile ? '24px' : isMobile ? '28px' : '32px',
      fontWeight: 700,
      color: '#dc3545'
    },
    originalPrice: {
      fontSize: isSmallMobile ? '18px' : isMobile ? '20px' : '24px',
      color: '#6c757d',
      textDecoration: 'line-through',
      marginLeft: '15px'
    },
    productOptions: {
      marginBottom: '30px'
    },
    colorSelection: {
      marginBottom: '20px'
    },
    quantitySelection: {
      marginBottom: '20px'
    },
    optionLabel: {
      display: 'block',
      fontWeight: 600,
      marginBottom: '10px',
      color: '#333'
    },
    colorOptions: {
      display: 'flex',
      gap: '10px',
      flexWrap: 'wrap' as const
    },
    colorOption: {
      padding: '8px 16px',
      border: '2px solid #e9ecef',
      borderRadius: '6px',
      backgroundColor: 'white',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      fontSize: '14px'
    },
    colorOptionSelected: {
      borderColor: '#fed700',
      backgroundColor: '#fed700',
      color: '#333',
      fontWeight: 600
    },
    quantityControls: {
      display: 'flex',
      alignItems: 'center',
      gap: '0',
      border: '2px solid #e9ecef',
      borderRadius: '6px',
      overflow: 'hidden',
      width: isSmallMobile ? '100%' : 'fit-content'
    },
    quantityBtn: {
      backgroundColor: '#f8f9fa',
      border: 'none',
      padding: '12px 16px',
      cursor: 'pointer',
      transition: 'background-color 0.3s ease',
      color: '#495057'
    },
    quantityBtnDisabled: {
      opacity: 0.5,
      cursor: 'not-allowed'
    },
    quantityDisplay: {
      padding: '12px 20px',
      backgroundColor: 'white',
      fontWeight: 600,
      minWidth: '60px',
      textAlign: 'center' as const,
      borderLeft: '1px solid #e9ecef',
      borderRight: '1px solid #e9ecef',
      flex: isSmallMobile ? 1 : 'none'
    },
    productActions: {
      display: 'flex',
      gap: '15px',
      flexWrap: 'wrap' as const,
      flexDirection: isMobile ? 'column' as const : 'row' as const
    },
    addToCartBtn: {
      backgroundColor: '#fed700',
      color: '#333',
      border: 'none',
      padding: '15px 30px',
      borderRadius: '6px',
      fontSize: '16px',
      fontWeight: 600,
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      display: 'flex',
      alignItems: 'center',
      gap: '10px',
      flex: 1,
      justifyContent: 'center',
      minWidth: isMobile ? '100%' : '180px'
    },
    actionBtn: {
      backgroundColor: 'white',
      color: '#6c757d',
      border: '2px solid #e9ecef',
      padding: '15px',
      borderRadius: '6px',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minWidth: '50px'
    },
    wishlistBtnActive: {
      backgroundColor: '#dc3545',
      color: 'white',
      borderColor: '#dc3545'
    },
    productTabs: {
      marginBottom: '40px'
    },
    tabHeaders: {
      display: 'flex',
      borderBottom: '2px solid #e9ecef',
      marginBottom: '30px',
      flexWrap: isMobile ? 'wrap' as const : 'nowrap' as const
    },
    tabHeader: {
      background: 'none',
      border: 'none',
      padding: '15px 25px',
      cursor: 'pointer',
      fontSize: '16px',
      fontWeight: 600,
      color: '#6c757d',
      transition: 'all 0.3s ease',
      borderBottom: '3px solid transparent',
      flex: isMobile ? 1 : 'none',
      minWidth: isMobile ? '120px' : 'auto',
      textAlign: isMobile ? 'center' as const : 'left' as const
    },
    tabHeaderActive: {
      color: '#fed700',
      borderBottomColor: '#fed700'
    },
    tabContent: {
      padding: '20px 0'
    },
    tabContentH3: {
      fontSize: '24px',
      fontWeight: 700,
      color: '#333',
      marginBottom: '20px'
    },
    descriptionP: {
      color: '#6c757d',
      lineHeight: 1.8,
      marginBottom: '15px'
    },
    specsTable: {
      width: '100%',
      borderCollapse: 'collapse' as const,
      backgroundColor: 'white',
      borderRadius: '8px',
      overflow: 'hidden',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
    },
    specsTableRowEven: {
      backgroundColor: '#f8f9fa'
    },
    specLabel: {
      padding: '15px 20px',
      fontWeight: 600,
      color: '#333',
      width: '30%',
      borderRight: '1px solid #e9ecef'
    },
    specValue: {
      padding: '15px 20px',
      color: '#6c757d'
    },
    reviewsSummary: {
      backgroundColor: '#f8f9fa',
      padding: '30px',
      borderRadius: '8px',
      marginBottom: '30px',
      textAlign: 'center' as const
    },
    averageRating: {
      display: 'flex',
      flexDirection: 'column' as const,
      alignItems: 'center'
    },
    ratingNumber: {
      fontSize: '48px',
      fontWeight: 700,
      color: '#333',
      marginBottom: '10px'
    },
    totalReviews: {
      color: '#6c757d',
      fontSize: '16px'
    },
    reviewsList: {
      display: 'flex',
      flexDirection: 'column' as const,
      gap: '25px'
    },
    reviewItem: {
      backgroundColor: 'white',
      padding: '25px',
      borderRadius: '8px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
    },
    reviewHeader: {
      display: 'flex',
      alignItems: 'center',
      gap: '15px',
      marginBottom: '15px',
      flexWrap: 'wrap' as const
    },
    reviewerName: {
      fontWeight: 600,
      color: '#333'
    },
    reviewDate: {
      color: '#6c757d',
      fontSize: '14px',
      marginLeft: 'auto'
    },
    reviewComment: {
      color: '#6c757d',
      lineHeight: 1.6
    },
    relatedProducts: {
      marginTop: '60px'
    },
    relatedProductsH2: {
      fontSize: '32px',
      fontWeight: 700,
      color: '#333',
      textAlign: 'center' as const,
      marginBottom: '40px'
    },
    relatedProductsGrid: {
      display: 'grid',
      gridTemplateColumns: isMobile ? 'repeat(auto-fit, minmax(200px, 1fr))' : 'repeat(auto-fit, minmax(250px, 1fr))',
      gap: isMobile ? '20px' : '30px'
    }
  };
  
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

  // Load related products when product is loaded
  useEffect(() => {
    const loadRelatedProducts = async () => {
      if (product && product.category) {
        try {
          // Get products from the same category
          const allProducts = await apiService.getAllProducts();
          const related = allProducts
            .filter((p: Product) => p.category === product.category && p.id !== product.id)
            .slice(0, 4);
          setRelatedProducts(related);
        } catch (error) {
          console.error('Error loading related products:', error);
        }
      }
    };

    loadRelatedProducts();
  }, [product]);

  // Set default color when product loads
  useEffect(() => {
    if (product && productDetails.colors.length > 0) {
      setSelectedColor(productDetails.colors[0]);
    }
  }, [product, productDetails.colors]);

  // Loading state
  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '400px',
        padding: '60px 20px',
        color: '#666'
      }}>
        <FontAwesomeIcon icon={faSpinner} spin style={{ fontSize: '2rem', marginBottom: '15px' }} />
        <h3 style={{ fontSize: '1.2rem', marginBottom: '10px' }}>Loading product...</h3>
        <p>Please wait while we fetch the product details</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '400px',
        padding: '60px 20px',
        color: '#dc3545',
        backgroundColor: '#f8d7da',
        borderRadius: '8px',
        border: '1px solid #f5c6cb',
        margin: '20px'
      }}>
        <h3 style={{ fontSize: '1.2rem', marginBottom: '10px' }}>Product not found</h3>
        <p style={{ marginBottom: '15px' }}>{error}</p>
        <Link
          to="/products"
          style={{
            backgroundColor: '#007bff',
            color: 'white',
            textDecoration: 'none',
            padding: '10px 20px',
            borderRadius: '5px',
            fontSize: '14px'
          }}
        >
          Back to Products
        </Link>
      </div>
    );
  }

  // Product not found
  if (!product) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '400px',
        padding: '60px 20px',
        color: '#666'
      }}>
        <h3 style={{ fontSize: '1.2rem', marginBottom: '10px' }}>Product not found</h3>
        <p style={{ marginBottom: '15px' }}>The requested product could not be found</p>
        <Link
          to="/products"
          style={{
            backgroundColor: '#007bff',
            color: 'white',
            textDecoration: 'none',
            padding: '10px 20px',
            borderRadius: '5px',
            fontSize: '14px'
          }}
        >
          Back to Products
        </Link>
      </div>
    );
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
    const stars: JSX.Element[] = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < fullStars; i++) {
      stars.push(<FontAwesomeIcon key={i} icon={faStar} style={styles.starFilled} />);
    }

    if (hasHalfStar) {
      stars.push(<FontAwesomeIcon key="half" icon={faStarHalfAlt} style={styles.starFilled} />);
    }

    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<FontAwesomeIcon key={`empty-${i}`} icon={faStar} style={styles.starEmpty} />);
    }

    return stars;
  };

  const averageRating = productDetails.reviews.reduce((acc, review) => acc + review.rating, 0) / productDetails.reviews.length;

  return (
    <div style={styles.productDetails}>
      {/* Breadcrumb */}
      <div style={styles.breadcrumb}>
        <Link to="/" style={styles.breadcrumbLink}>Home</Link>
        <span> / </span>
        <Link to="/products" style={styles.breadcrumbLink}>Products</Link>
        <span> / </span>
        <span>{product.category}</span>
        <span> / </span>
        <span>{product.name}</span>
      </div>

      {/* Main Product Section */}
      <div style={styles.productMain}>
        {/* Product Images */}
        <div style={styles.productImages}>
          <div style={styles.mainImage}>
            <img 
              src={productDetails.images[selectedImage]} 
              alt={product.name}
              style={styles.mainProductImage}
            />
          </div>
          <div style={styles.imageThumbnails}>
            {productDetails.images.map((image, index) => (
              <img
                key={index}
                src={image}
                alt={`${product.name} ${index + 1}`}
                style={{
                  ...styles.thumbnail,
                  ...(selectedImage === index ? styles.thumbnailActive : {})
                }}
                onClick={() => setSelectedImage(index)}
              />
            ))}
          </div>
        </div>

        {/* Product Info */}
        <div style={styles.productInfo}>
          <div style={styles.productCategory}>{product.category}</div>
          <h1 style={styles.productTitle}>{product.name}</h1>
          
          {/* Rating */}
          <div style={styles.productRating}>
            <div style={styles.stars}>
              {renderStars(averageRating)}
            </div>
            <span style={styles.ratingText}>
              ({productDetails.reviews.length} customer reviews)
            </span>
          </div>

          {/* Availability */}
          <div style={styles.productAvailability}>
            <FontAwesomeIcon icon={faCheck} style={styles.checkIcon} />
            <span>Availability: {productDetails.stock} in stock</span>
          </div>

          {/* Features */}
          <div style={styles.productFeatures}>
            {productDetails.features.map((feature, index) => (
              <div key={index} style={styles.featureItem}>
                • {feature}
              </div>
            ))}
          </div>

          {/* Description */}
          <div style={styles.productShortDescription}>
            {productDetails.description.split('\n')[0]}
          </div>

          {/* SKU */}
          <div style={styles.productSku}>
            <strong>SKU:</strong> {productDetails.sku}
          </div>

          {/* Price */}
          <div style={styles.productPrice}>
            <span style={styles.currentPrice}>${product.price}</span>
            {product.originalPrice && (
              <span style={styles.originalPrice}>${product.originalPrice}</span>
            )}
          </div>

          {/* Color Selection */}
          <div style={styles.productOptions}>
            <div style={styles.colorSelection}>
              <label style={styles.optionLabel}>Color:</label>
              <div style={styles.colorOptions}>
                {productDetails.colors.map((color) => (
                  <button
                    key={color}
                    style={{
                      ...styles.colorOption,
                      ...(selectedColor === color ? styles.colorOptionSelected : {})
                    }}
                    onClick={() => setSelectedColor(color)}
                    title={color}
                  >
                    {color}
                  </button>
                ))}
              </div>
            </div>

            {/* Quantity Selection */}
            <div style={styles.quantitySelection}>
              <label style={styles.optionLabel}>Quantity:</label>
              <div style={styles.quantityControls}>
                <button 
                  style={{
                    ...styles.quantityBtn,
                    ...(quantity <= 1 ? styles.quantityBtnDisabled : {})
                  }}
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  disabled={quantity <= 1}
                >
                  <FontAwesomeIcon icon={faMinus} />
                </button>
                <span style={styles.quantityDisplay}>{quantity}</span>
                <button 
                  style={{
                    ...styles.quantityBtn,
                    ...(quantity >= productDetails.stock ? styles.quantityBtnDisabled : {})
                  }}
                  onClick={() => setQuantity(Math.min(productDetails.stock, quantity + 1))}
                  disabled={quantity >= productDetails.stock}
                >
                  <FontAwesomeIcon icon={faPlus} />
                </button>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div style={styles.productActions}>
            <button style={styles.addToCartBtn} onClick={handleAddToCart}>
              <FontAwesomeIcon icon={faShoppingCart} />
              Add to Cart
            </button>
            <button 
              style={{
                ...styles.actionBtn,
                ...(isInWishlist(product.id) ? styles.wishlistBtnActive : {})
              }}
              onClick={handleAddToWishlist}
            >
              <FontAwesomeIcon icon={faHeart} />
              Wishlist
            </button>
            <button style={styles.actionBtn}>
              <FontAwesomeIcon icon={faCompressArrowsAlt} />
              Compare
            </button>
            <button style={styles.actionBtn}>
              <FontAwesomeIcon icon={faShareAlt} />
              Share
            </button>
          </div>
        </div>
      </div>

      {/* Product Details Tabs */}
      <div style={styles.productTabs}>
        <div style={styles.tabHeaders}>
          <button 
            style={{
              ...styles.tabHeader,
              ...(activeTab === 'description' ? styles.tabHeaderActive : {})
            }}
            onClick={() => setActiveTab('description')}
          >
            Description
          </button>
          <button 
            style={{
              ...styles.tabHeader,
              ...(activeTab === 'specifications' ? styles.tabHeaderActive : {})
            }}
            onClick={() => setActiveTab('specifications')}
          >
            Specifications
          </button>
          <button 
            style={{
              ...styles.tabHeader,
              ...(activeTab === 'reviews' ? styles.tabHeaderActive : {})
            }}
            onClick={() => setActiveTab('reviews')}
          >
            Reviews ({productDetails.reviews.length})
          </button>
        </div>

        <div style={styles.tabContent}>
          {activeTab === 'description' && (
            <div>
              <h3 style={styles.tabContentH3}>Product Description</h3>
              {productDetails.description.split('\n').map((paragraph, index) => (
                <p key={index} style={styles.descriptionP}>{paragraph}</p>
              ))}
            </div>
          )}

          {activeTab === 'specifications' && (
            <div>
              <h3 style={styles.tabContentH3}>Product Specifications</h3>
              <table style={styles.specsTable}>
                <tbody>
                  {Object.entries(productDetails.specifications).map(([key, value], index) => (
                    <tr key={key} style={index % 2 === 1 ? styles.specsTableRowEven : {}}>
                      <td style={styles.specLabel}>{key}</td>
                      <td style={styles.specValue}>{value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'reviews' && (
            <div>
              <h3 style={styles.tabContentH3}>Customer Reviews</h3>
              <div style={styles.reviewsSummary}>
                <div style={styles.averageRating}>
                  <div style={styles.ratingNumber}>{averageRating.toFixed(1)}</div>
                  <div style={styles.stars}>
                    {renderStars(averageRating)}
                  </div>
                  <div style={styles.totalReviews}>Based on {productDetails.reviews.length} reviews</div>
                </div>
              </div>
              
              <div style={styles.reviewsList}>
                {productDetails.reviews.map((review) => (
                  <div key={review.id} style={styles.reviewItem}>
                    <div style={styles.reviewHeader}>
                      <div style={styles.reviewerName}>{review.name}</div>
                      <div style={styles.stars}>
                        {renderStars(review.rating)}
                      </div>
                      <div style={styles.reviewDate}>{new Date(review.date).toLocaleDateString()}</div>
                    </div>
                    <div style={styles.reviewComment}>{review.comment}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Related Products */}
      {relatedProducts.length > 0 && (
        <div style={styles.relatedProducts}>
          <h2 style={styles.relatedProductsH2}>Related Products</h2>
          <div style={styles.relatedProductsGrid}>
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
        <div style={{ maxWidth: '1430px', margin: '0 auto', padding: '0 1rem' }}>
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
