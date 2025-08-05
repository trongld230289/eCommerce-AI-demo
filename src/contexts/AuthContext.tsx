import React, { createContext, useContext, useEffect, useState } from 'react';
import { User } from '../types';
import { getMockUserByEmail } from '../utils/mockUsers';

interface AuthContextType {
  currentUser: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, displayName?: string) => Promise<void>;
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

  // Helper function to generate userId for compatibility with backend
  const generateUserId = (email: string): string => {
    // Check if this is a predefined mock user
    const mockUser = getMockUserByEmail(email);
    if (mockUser) {
      return mockUser.userId;
    }
    
    // Generate a simple user ID based on email for new users
    const emailHash = btoa(email).replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
    return emailHash.substring(0, 8);
  };

  const login = async (email: string, password: string) => {
    // Check if this is a mock user with correct password
    const mockUser = getMockUserByEmail(email);
    if (mockUser && mockUser.password === password) {
      const user: User = {
        uid: mockUser.userId,
        email: mockUser.email,
        displayName: mockUser.displayName
      };
      setCurrentUser(user);
      localStorage.setItem('currentUser', JSON.stringify(user));
      return;
    }
    
    // Throw error for invalid credentials
    throw new Error('Invalid email or password');
  };

  const register = async (email: string, password: string, displayName?: string) => {
    // Check if this email is already a mock user
    const mockUser = getMockUserByEmail(email);
    if (mockUser) {
      // For demo purposes, just log them in if credentials match
      if (mockUser.password === password) {
        const user: User = {
          uid: mockUser.userId,
          email: mockUser.email,
          displayName: mockUser.displayName
        };
        setCurrentUser(user);
        localStorage.setItem('currentUser', JSON.stringify(user));
        return;
      } else {
        throw new Error('Email already exists with different password');
      }
    }
    
    // For new registrations, create new user
    const user: User = { 
      uid: generateUserId(email),
      email, 
      displayName: displayName || email.split('@')[0]
    };
    setCurrentUser(user);
    localStorage.setItem('currentUser', JSON.stringify(user));
  };

  const logout = async () => {
    setCurrentUser(null);
    localStorage.removeItem('currentUser');
  };

  useEffect(() => {
    // Check for stored user on component mount
    const storedUser = localStorage.getItem('currentUser');
    if (storedUser) {
      try {
        setCurrentUser(JSON.parse(storedUser));
      } catch (error) {
        console.error('Error parsing stored user:', error);
        localStorage.removeItem('currentUser');
      }
    }
    setLoading(false);
  }, []);

  const value: AuthContextType = {
    currentUser,
    loading,
    login,
    register,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
