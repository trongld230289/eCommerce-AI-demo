import { createContext, useContext, useReducer, ReactNode, useEffect, useState } from 'react';
import { useAuth } from './AuthContext';

export interface Product {
  id: number;
  name: string;
  price: number;
  originalPrice?: number;
  image: string;
  category: string;
  description?: string;
  brand?: string;
  tags?: string[];
  color?: string;
  size?: string;
  rating?: number;
  isNew?: boolean;
  discount?: number;
}

export interface CartItem extends Product {
  quantity: number;
}

interface ShopState {
  cart: CartItem[];
  wishlist: Product[];
}

type ShopAction =
  | { type: 'ADD_TO_CART'; payload: Product }
  | { type: 'REMOVE_FROM_CART'; payload: number }
  | { type: 'UPDATE_QUANTITY'; payload: { id: number; quantity: number } }
  | { type: 'CLEAR_CART' }
  | { type: 'ADD_TO_WISHLIST'; payload: Product }
  | { type: 'REMOVE_FROM_WISHLIST'; payload: number }
  | { type: 'LOAD_USER_DATA'; payload: ShopState };

const initialState: ShopState = {
  cart: [],
  wishlist: []
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

  // Load user data from localStorage when user changes
  useEffect(() => {
    if (currentUser) {
      const userDataKey = `shop_data_${currentUser.uid}`;
      const savedData = localStorage.getItem(userDataKey);
      console.log('Loading user data for:', currentUser.uid, 'Data:', savedData);
      if (savedData) {
        try {
          const parsedData = JSON.parse(savedData);
          console.log('Parsed data:', parsedData);
          dispatch({ type: 'LOAD_USER_DATA', payload: parsedData });
        } catch (error) {
          console.error('Error loading user shop data:', error);
        }
      }
      setIsInitialized(true);
    } else {
      // Clear state when user logs out
      console.log('User logged out, clearing state');
      dispatch({ type: 'LOAD_USER_DATA', payload: initialState });
      setIsInitialized(false);
    }
  }, [currentUser]);

  // Save user data to localStorage whenever state changes (but not during initial load)
  useEffect(() => {
    if (currentUser && isInitialized) {
      const userDataKey = `shop_data_${currentUser.uid}`;
      console.log('Saving user data for:', currentUser.uid, 'State:', state);
      localStorage.setItem(userDataKey, JSON.stringify(state));
    }
  }, [state, currentUser, isInitialized]);

  const addToCart = (product: Product) => {
    dispatch({ type: 'ADD_TO_CART', payload: product });
  };

  const removeFromCart = (productId: number) => {
    dispatch({ type: 'REMOVE_FROM_CART', payload: productId });
  };

  const updateQuantity = (productId: number, quantity: number) => {
    if (quantity <= 0) {
      removeFromCart(productId);
    } else {
      dispatch({ type: 'UPDATE_QUANTITY', payload: { id: productId, quantity } });
    }
  };

  const clearCart = () => {
    dispatch({ type: 'CLEAR_CART' });
  };

  const addToWishlist = (product: Product) => {
    dispatch({ type: 'ADD_TO_WISHLIST', payload: product });
  };

  const removeFromWishlist = (productId: number) => {
    dispatch({ type: 'REMOVE_FROM_WISHLIST', payload: productId });
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