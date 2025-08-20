import React, { createContext, useContext, useEffect, useState } from 'react';
import { 
  User as FirebaseUser,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  updateProfile,
  signInWithPopup
} from 'firebase/auth';
import { auth, googleProvider } from '../utils/firebase';
import { User } from '../types';

interface AuthContextType {
  currentUser: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, displayName?: string) => Promise<void>;
  loginWithGoogle: () => Promise<{ isNewUser: boolean }>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const login = async (email: string, password: string) => {
    try {
      await signInWithEmailAndPassword(auth, email, password);
    } catch (error: any) {
      console.error('Login error:', error);
      if (error.code === 'auth/configuration-not-found') {
        console.error('Firebase Auth configuration error: Email/Password authentication is not enabled in Firebase Console');
      }
      throw error;
    }
  };

  const register = async (email: string, password: string, displayName?: string) => {
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      if (displayName) {
        await updateProfile(userCredential.user, { displayName });
      }
    } catch (error: any) {
      console.error('Registration error:', error);
      if (error.code === 'auth/configuration-not-found') {
        console.error('Firebase Auth configuration error: Email/Password authentication is not enabled in Firebase Console');
      }
      throw error;
    }
  };

  const loginWithGoogle = async () => {
    try {
      const result = await signInWithPopup(auth, googleProvider);
      console.log('Google sign-in successful:', result.user);
      
      // Check if this is a new user by looking at the user creation time
      const isNewUser = result.user.metadata.creationTime === result.user.metadata.lastSignInTime;
      console.log('Is new user:', isNewUser);
      
      return { isNewUser };
    } catch (error: any) {
      console.error('Google sign-in error:', error);
      if (error.code === 'auth/configuration-not-found') {
        console.error('Firebase Auth configuration error: Google authentication is not enabled in Firebase Console');
      }
      throw error;
    }
  };

  const logout = async () => {
    try {
      await signOut(auth);
    } catch (error: any) {
      console.error('Logout error:', error);
      throw error;
    }
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user: FirebaseUser | null) => {
      if (user) {
        // Store user ID in localStorage for API calls
        localStorage.setItem('userId', user.uid);
        localStorage.setItem('user_id', user.uid); // Also store as user_id for compatibility
        
        setCurrentUser({
          uid: user.uid,
          email: user.email || '',
          displayName: user.displayName || undefined,
          photoURL: user.photoURL || undefined
        });
      } else {
        // Clear user ID from localStorage on logout
        localStorage.removeItem('userId');
        localStorage.removeItem('user_id');
        setCurrentUser(null);
      }
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const value: AuthContextType = {
    currentUser,
    loading,
    login,
    register,
    loginWithGoogle,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
