import React from 'react';
import { useShop } from './ShopContext';
import { Link } from 'react-router-dom';
import SimpleProductCard from './SimpleProductCard';

const Wishlist = () => {
  const { wishlist, removeFromWishlist, addToCart } = useShop();

  if (wishlist.length === 0) {
    return (
      <div style={{
        maxWidth: '1340px',
        margin: '0 auto',
        padding: '4rem 1rem',
        textAlign: 'center',
        fontFamily: 'Open Sans, Arial, sans-serif'
      }}>
        <h2 style={{
          fontSize: '2rem',
          marginBottom: '1rem',
          color: '#2c3e50'
        }}>
          Your Wishlist is Empty
        </h2>
        <p style={{
          fontSize: '1.1rem',
          color: '#6c757d',
          marginBottom: '2rem'
        }}>
          Save items you love for later!
        </p>
        <Link
          to="/products"
          style={{
            backgroundColor: '#fed700',
            color: '#333333',
            padding: '1rem 2rem',
            borderRadius: '4px',
            textDecoration: 'none',
            fontWeight: '600',
            display: 'inline-block'
          }}
        >
          Continue Shopping
        </Link>
      </div>
    );
  }

  const handleAddToCart = (product: any) => {
    addToCart(product);
    alert(`Added ${product.name} to cart!`);
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
        My Wishlist
      </h1>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
        gap: '2rem'
      }}>
        {wishlist.map((product) => (
          <SimpleProductCard
            key={product.id}
            product={product}
            onAddToCart={handleAddToCart}
            onAddToWishlist={() => removeFromWishlist(product.id)}
            isInWishlist={() => true}
          />
        ))}
      </div>

      <div style={{
        textAlign: 'center',
        marginTop: '3rem'
      }}>
        <Link
          to="/products"
          style={{
            backgroundColor: '#2c3e50',
            color: 'white',
            padding: '1rem 2rem',
            borderRadius: '4px',
            textDecoration: 'none',
            fontWeight: '600',
            display: 'inline-block'
          }}
        >
          Continue Shopping
        </Link>
      </div>
    </div>
  );
};

export default Wishlist;
