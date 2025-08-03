import React from 'react';
import { useShop } from './ShopContext';
import SimpleProductCard from './SimpleProductCard';

const Products = () => {
  const { addToCart, addToWishlist, isInWishlist } = useShop();

  const products = [
    { 
      id: 1, 
      name: 'Wireless Audio System Multiroom 360 degree Full...', 
      price: 685, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg', 
      category: 'Speakers', 
      description: 'Wireless Audio System Multiroom 360 degree Full base audio system', 
      rating: 5, 
      isNew: false, 
      originalPrice: 799, 
      discount: 114 
    },
    { 
      id: 2, 
      name: 'Tablet White EliteBook Revolve 810 G2', 
      price: 1999, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg', 
      category: 'Laptops', 
      description: 'Tablet White EliteBook Revolve 810 G2 with touchscreen', 
      rating: 5, 
      isNew: false, 
      originalPrice: 2299, 
      discount: 300 
    },
    { 
      id: 3, 
      name: 'Purple Solo 2 Wireless', 
      price: 685, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg', 
      category: 'Headphones', 
      description: 'Purple Solo 2 Wireless headphones with premium sound', 
      rating: 4, 
      isNew: false, 
      originalPrice: 799, 
      discount: 114 
    },
    { 
      id: 4, 
      name: 'Smartphone 6S 32GB LTE', 
      price: 685, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg', 
      category: 'Smartphones', 
      description: 'Smartphone 6S 32GB LTE with advanced camera', 
      rating: 5, 
      isNew: false, 
      originalPrice: 799, 
      discount: 114 
    },
    { 
      id: 5, 
      name: 'Widescreen NX Mini F1 SMART NX', 
      price: 685, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg', 
      category: 'Cameras', 
      description: 'Widescreen NX Mini F1 SMART NX professional camera', 
      rating: 4, 
      isNew: true, 
      originalPrice: 799, 
      discount: 114 
    },
    { 
      id: 6, 
      name: 'Full Color LaserJet Pro M452dn', 
      price: 685, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg', 
      category: 'Printers', 
      description: 'Full Color LaserJet Pro M452dn high-quality printer', 
      rating: 5, 
      isNew: false, 
      originalPrice: 799, 
      discount: 114 
    },
    { 
      id: 7, 
      name: 'Game Console Controller + USB 3.0 Cable', 
      price: 79, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg', 
      category: 'Gaming', 
      description: 'Wireless game controller with USB 3.0 cable', 
      rating: 4, 
      isNew: false, 
      originalPrice: 99, 
      discount: 20 
    },
    { 
      id: 8, 
      name: 'Camera C430W 4k Waterproof', 
      price: 685, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg', 
      category: 'Cameras', 
      description: 'Camera C430W 4k Waterproof action camera', 
      rating: 5, 
      isNew: true, 
      originalPrice: 799, 
      discount: 114 
    },
    { 
      id: 9, 
      name: 'Smart TV 55" 4K Ultra HD', 
      price: 1299, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg', 
      category: 'TV & Audio', 
      description: 'Smart TV 55 inch 4K Ultra HD with HDR', 
      rating: 5, 
      isNew: true, 
      originalPrice: 1499, 
      discount: 200 
    },
    { 
      id: 10, 
      name: 'Wireless Bluetooth Earbuds', 
      price: 149, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg', 
      category: 'Headphones', 
      description: 'Premium wireless Bluetooth earbuds with noise cancellation', 
      rating: 4, 
      isNew: false, 
      originalPrice: 199, 
      discount: 50 
    },
    { 
      id: 11, 
      name: 'Gaming Mechanical Keyboard', 
      price: 129, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg', 
      category: 'Gaming', 
      description: 'RGB mechanical gaming keyboard with custom switches', 
      rating: 5, 
      isNew: false, 
      originalPrice: 179, 
      discount: 50 
    },
    { 
      id: 12, 
      name: 'Professional DSLR Camera', 
      price: 2499, 
      image: 'https://transvelo.github.io/electro-html/2.0/assets/img/212X200/img2.jpg', 
      category: 'Cameras', 
      description: 'Professional DSLR camera with 24MP sensor', 
      rating: 5, 
      isNew: true, 
      originalPrice: 2799, 
      discount: 300 
    }
  ];

  const handleAddToCart = (product: any) => {
    addToCart(product);
    alert(`Added ${product.name} to cart!`);
  };

  const handleAddToWishlist = (product: any) => {
    if (isInWishlist(product.id)) {
      alert(`${product.name} is already in wishlist!`);
    } else {
      addToWishlist(product);
      alert(`Added ${product.name} to wishlist!`);
    }
  };

  return (
    <div style={{
      maxWidth: '1340px',
      margin: '0 auto',
      padding: '2rem 1rem',
      fontFamily: 'Open Sans, Arial, sans-serif'
    }}>
      <h1 style={{
        fontSize: '2.5rem',
        marginBottom: '2rem',
        color: '#2c3e50',
        textAlign: 'center'
      }}>
        All Products
      </h1>

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
            onAddToWishlist={handleAddToWishlist}
            isInWishlist={isInWishlist}
          />
        ))}
      </div>
    </div>
  );
};

export default Products;
