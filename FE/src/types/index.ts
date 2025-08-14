export interface Product {
  id: number;
  name: string;
  price: number;
  original_price?: number;
  imageUrl: string;
  category: string;
  description?: string;
  rating?: number;
  discount?: number;
}

export interface CartItem {
  product: Product;
  quantity: number;
}

export interface WishlistItem {
  product: Product;
  addedAt: Date;
}

export interface User {
  uid: string;
  email: string;
  displayName?: string;
  photoURL?: string;
}

export interface FilterOptions {
  category?: string;
  brand?: string;
  minPrice?: number;
  maxPrice?: number;
  inStock?: boolean;
}

export interface SearchIntent {
  category?: string;
  brand?: string;
  price_min?: number;
  price_max?: number;
  keywords?: string[];
}
