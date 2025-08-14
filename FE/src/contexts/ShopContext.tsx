import { createContext, useContext, useReducer, ReactNode, useEffect, useState } from 'react';
import { useAuth } from './AuthContext';
import { eventTrackingService } from '../services/eventTrackingService';
import { cartService } from '../services/cartService';

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

export interface CartItem extends Product {
  quantity: number;
}

interface ShopState {
  cart: CartItem[];
  wishlist: Product[];
  isLoading: boolean;
}

type ShopAction =
  | { type: 'ADD_TO_CART'; payload: Product }
  | { type: 'REMOVE_FROM_CART'; payload: number }
  | { type: 'UPDATE_QUANTITY'; payload: { id: number; quantity: number } }
  | { type: 'CLEAR_CART' }
  | { type: 'ADD_TO_WISHLIST'; payload: Product }
  | { type: 'REMOVE_FROM_WISHLIST'; payload: number }
  | { type: 'LOAD_USER_DATA'; payload: ShopState }
  | { type: 'LOAD_CART_FROM_FIREBASE'; payload: CartItem[] }
  | { type: 'SET_LOADING'; payload: boolean };

const initialState: ShopState = {
  cart: [],
  wishlist: [],
  isLoading: false
};

const shopReducer = (state: ShopState, action: ShopAction): ShopState => {
  switch (action.type) {
    case 'ADD_TO_CART': {
      const existingItem = state.cart.find(item => item.id === action.payload.id);
      if (existingItem) {
        return {
          ...state,
          cart: state.cart.map(item =>
            item.id === action.payload.id
              ? { ...item, quantity: item.quantity + 1 }
              : item
          )
        };
      }
      return {
        ...state,
        cart: [...state.cart, { ...action.payload, quantity: 1 }]
      };
    }
    
    case 'REMOVE_FROM_CART':
      return {
        ...state,
        cart: state.cart.filter(item => item.id !== action.payload)
      };
    
    case 'UPDATE_QUANTITY':
      return {
        ...state,
        cart: state.cart.map(item =>
          item.id === action.payload.id
            ? { ...item, quantity: action.payload.quantity }
            : item
        )
      };
    
    case 'CLEAR_CART':
      return {
        ...state,
        cart: []
      };
    
    case 'ADD_TO_WISHLIST': {
      const isInWishlist = state.wishlist.some(item => item.id === action.payload.id);
      if (isInWishlist) return state;
      return {
        ...state,
        wishlist: [...state.wishlist, action.payload]
      };
    }
    
    case 'REMOVE_FROM_WISHLIST':
      return {
        ...state,
        wishlist: state.wishlist.filter(item => item.id !== action.payload)
      };
    
    case 'LOAD_USER_DATA':
      return action.payload;
    
    case 'LOAD_CART_FROM_FIREBASE':
      return {
        ...state,
        cart: action.payload,
        isLoading: false
      };
    
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload
      };
    
    default:
      return state;
  }
};

interface ShopContextType {
  state: ShopState;
  addToCart: (product: Product) => void;
  removeFromCart: (productId: number) => void;
  updateQuantity: (productId: number, quantity: number) => void;
  clearCart: () => void;
  addToWishlist: (product: Product) => void;
  removeFromWishlist: (productId: number) => void;
  getCartTotal: () => number;
  getCartItemsCount: () => number;
  isInWishlist: (productId: number) => boolean;
}

const ShopContext = createContext<ShopContextType | undefined>(undefined);

export const useShop = () => {
  const context = useContext(ShopContext);
  if (!context) {
    throw new Error('useShop must be used within a ShopProvider');
  }
  return context;
};

interface ShopProviderProps {
  children: ReactNode;
}

export const ShopProvider = ({ children }: ShopProviderProps) => {
  const [state, dispatch] = useReducer(shopReducer, initialState);
  const [isInitialized, setIsInitialized] = useState(false);
  const { currentUser } = useAuth();

  // Load cart from Firebase when user changes
  useEffect(() => {
    const loadCartFromFirebase = async () => {
      if (currentUser) {
        try {
          dispatch({ type: 'SET_LOADING', payload: true });
          
          // First, try to sync any localStorage cart data to Firebase
          const userDataKey = `shop_data_${currentUser.uid}`;
          const savedData = localStorage.getItem(userDataKey);
          
          if (savedData) {
            try {
              const parsedData = JSON.parse(savedData);
              if (parsedData.cart && parsedData.cart.length > 0) {
                console.log('Syncing localStorage cart to Firebase:', parsedData.cart);
                await cartService.syncCartFromLocalStorage(currentUser.uid, parsedData.cart);
                // Clear localStorage after sync
                localStorage.removeItem(userDataKey);
              }
            } catch (error) {
              console.error('Error syncing localStorage cart:', error);
            }
          }
          
          // Load cart from Firebase
          console.log('Loading cart from Firebase for user:', currentUser.uid);
          const firebaseCart = await cartService.getCart(currentUser.uid);
          
          // Convert Firebase cart to frontend format
          const cartItems: CartItem[] = firebaseCart.items.map((item: any) => ({
            id: item.product_details.id,
            name: item.product_details.name,
            price: item.product_details.price,
            original_price: item.product_details.original_price,
            imageUrl: item.product_details.imageUrl,
            category: item.product_details.category,
            description: item.product_details.description,
            rating: item.product_details.rating,
            discount: item.product_details.discount,
            quantity: item.quantity
          }));
          
          dispatch({ type: 'LOAD_CART_FROM_FIREBASE', payload: cartItems });
          
          // Load wishlist from localStorage (keeping existing functionality)
          const wishlistData = localStorage.getItem(`wishlist_${currentUser.uid}`);
          if (wishlistData) {
            try {
              const parsedWishlist = JSON.parse(wishlistData);
              dispatch({ type: 'LOAD_USER_DATA', payload: { cart: cartItems, wishlist: parsedWishlist, isLoading: false } });
            } catch (error) {
              console.error('Error loading wishlist:', error);
            }
          }
          
          setIsInitialized(true);
        } catch (error) {
          console.error('Error loading cart from Firebase:', error);
          dispatch({ type: 'SET_LOADING', payload: false });
          setIsInitialized(true);
        }
      } else {
        // Clear state when user logs out
        console.log('User logged out, clearing state');
        dispatch({ type: 'LOAD_USER_DATA', payload: initialState });
        setIsInitialized(false);
      }
    };

    loadCartFromFirebase();
  }, [currentUser]); // Remove state from dependencies

  // Save wishlist to localStorage whenever it changes
  useEffect(() => {
    if (currentUser && isInitialized && state.wishlist) {
      const wishlistKey = `wishlist_${currentUser.uid}`;
      localStorage.setItem(wishlistKey, JSON.stringify(state.wishlist));
    }
  }, [state.wishlist, currentUser, isInitialized]);

  const addToCart = async (product: Product) => {
    if (!currentUser) {
      // If not logged in, use local state
      dispatch({ type: 'ADD_TO_CART', payload: product });
      return;
    }

    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      
      // Add to Firebase with product details
      const updatedCart = await cartService.addItemToCart(currentUser.uid, product.id, 1, product);
      
      // Convert to frontend format and update state
      const cartItems: CartItem[] = updatedCart.items.map((item: any) => ({
        id: item.product_details.id,
        name: item.product_details.name,
        price: item.product_details.price,
        original_price: item.product_details.original_price,
        imageUrl: item.product_details.imageUrl,
        category: item.product_details.category,
        description: item.product_details.description,
        rating: item.product_details.rating,
        discount: item.product_details.discount,
        quantity: item.quantity
      }));
      
      dispatch({ type: 'LOAD_CART_FROM_FIREBASE', payload: cartItems });
      
      // Track add to cart event - DISABLED to avoid duplicate tracking (handled by useRecommendations hook)
      // eventTrackingService.trackAddToCart(currentUser.uid, product.id.toString(), {
      //   product_name: product.name,
      //   product_category: product.category,
      //   product_brand: 'Unknown',
      //   product_price: product.price,
      // }).catch(error => {
      //   console.error('Failed to track add to cart event:', error);
      // });
    } catch (error) {
      console.error('Error adding item to cart:', error);
      dispatch({ type: 'SET_LOADING', payload: false });
      // Fallback to local state if Firebase fails
      dispatch({ type: 'ADD_TO_CART', payload: product });
    }
  };

  const removeFromCart = async (productId: number) => {
    if (!currentUser) {
      // If not logged in, use local state
      dispatch({ type: 'REMOVE_FROM_CART', payload: productId });
      return;
    }

    try {
      // Find the product before removing for event tracking
      const product = state.cart.find(item => item.id === productId);
      
      dispatch({ type: 'SET_LOADING', payload: true });
      
      // Remove from Firebase
      const updatedCart = await cartService.removeItemFromCart(currentUser.uid, productId);
      
      // Convert to frontend format and update state
      const cartItems: CartItem[] = updatedCart.items.map((item: any) => ({
        id: item.product_details.id,
        name: item.product_details.name,
        price: item.product_details.price,
        original_price: item.product_details.original_price,
        imageUrl: item.product_details.imageUrl,
        category: item.product_details.category,
        description: item.product_details.description,
        rating: item.product_details.rating,
        discount: item.product_details.discount,
        quantity: item.quantity
      }));
      
      dispatch({ type: 'LOAD_CART_FROM_FIREBASE', payload: cartItems });
      
      // Track remove from cart event
      if (product) {
        eventTrackingService.trackRemoveFromCart(currentUser.uid, productId.toString(), {
          product_name: product.name,
          product_category: product.category,
          product_brand: 'Unknown',
          product_price: product.price,
        }).catch(error => {
          console.error('Failed to track remove from cart event:', error);
        });
      }
    } catch (error) {
      console.error('Error removing item from cart:', error);
      dispatch({ type: 'SET_LOADING', payload: false });
      // Fallback to local state if Firebase fails
      dispatch({ type: 'REMOVE_FROM_CART', payload: productId });
    }
  };

  const updateQuantity = async (productId: number, quantity: number) => {
    if (quantity <= 0) {
      await removeFromCart(productId);
      return;
    }

    if (!currentUser) {
      // If not logged in, use local state
      dispatch({ type: 'UPDATE_QUANTITY', payload: { id: productId, quantity } });
      return;
    }

    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      
      // Update in Firebase
      const updatedCart = await cartService.updateItemQuantity(currentUser.uid, productId, quantity);
      
      // Convert to frontend format and update state
      const cartItems: CartItem[] = updatedCart.items.map((item: any) => ({
        id: item.product_details.id,
        name: item.product_details.name,
        price: item.product_details.price,
        original_price: item.product_details.original_price,
        imageUrl: item.product_details.imageUrl,
        category: item.product_details.category,
        description: item.product_details.description,
        rating: item.product_details.rating,
        discount: item.product_details.discount,
        quantity: item.quantity
      }));
      
      dispatch({ type: 'LOAD_CART_FROM_FIREBASE', payload: cartItems });
    } catch (error) {
      console.error('Error updating cart item quantity:', error);
      dispatch({ type: 'SET_LOADING', payload: false });
      // Fallback to local state if Firebase fails
      dispatch({ type: 'UPDATE_QUANTITY', payload: { id: productId, quantity } });
    }
  };

  const clearCart = async () => {
    if (!currentUser) {
      // If not logged in, use local state
      dispatch({ type: 'CLEAR_CART' });
      return;
    }

    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      
      // Clear in Firebase
      await cartService.clearCart(currentUser.uid);
      
      // Update state
      dispatch({ type: 'LOAD_CART_FROM_FIREBASE', payload: [] });
    } catch (error) {
      console.error('Error clearing cart:', error);
      dispatch({ type: 'SET_LOADING', payload: false });
      // Fallback to local state if Firebase fails
      dispatch({ type: 'CLEAR_CART' });
    }
  };

  const addToWishlist = (product: Product) => {
    dispatch({ type: 'ADD_TO_WISHLIST', payload: product });
    
    // Track add to wishlist event
    if (currentUser) {
      eventTrackingService.trackAddToWishlist(currentUser.uid, product.id.toString(), {
        product_name: product.name,
        product_category: product.category,
        product_brand: 'Unknown',
        product_price: product.price,
      }).catch(error => {
        console.error('Failed to track add to wishlist event:', error);
      });
    }
  };

  const removeFromWishlist = (productId: number) => {
    // Find the product before removing for event tracking
    const product = state.wishlist.find(item => item.id === productId);
    
    dispatch({ type: 'REMOVE_FROM_WISHLIST', payload: productId });
    
    // Track remove from wishlist event
    if (currentUser && product) {
      eventTrackingService.trackRemoveFromWishlist(currentUser.uid, productId.toString(), {
        product_name: product.name,
        product_category: product.category,
        product_brand: 'Unknown',
        product_price: product.price,
      }).catch(error => {
        console.error('Failed to track remove from wishlist event:', error);
      });
    }
  };

  const getCartTotal = () => {
    return state.cart.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  const getCartItemsCount = () => {
    return state.cart.reduce((total, item) => total + item.quantity, 0);
  };

  const isInWishlist = (productId: number) => {
    return state.wishlist.some(item => item.id === productId);
  };

  const value: ShopContextType = {
    state,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    addToWishlist,
    removeFromWishlist,
    getCartTotal,
    getCartItemsCount,
    isInWishlist
  };

  return (
    <ShopContext.Provider value={value}>
      {children}
    </ShopContext.Provider>
  );
};
