import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getMockUserByEmail } from '../utils/mockUsers';

interface User {
  id: string;
  email: string;
  displayName?: string;
}

interface AuthContextType {
  currentUser: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const useAuth = () => useContext(AuthContext);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  useEffect(() => {
    // Check for stored user on component mount
    const storedUser = localStorage.getItem('currentUser');
    if (storedUser) {
      setCurrentUser(JSON.parse(storedUser));
    }
  }, []);

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
        id: mockUser.userId,
        email: mockUser.email,
        displayName: mockUser.displayName
      };
      setCurrentUser(user);
      localStorage.setItem('currentUser', JSON.stringify(user));
      return;
    }
    
    // For demo purposes, allow any email/password combination
    const user: User = { 
      id: generateUserId(email),
      email, 
      displayName: email.split('@')[0] 
    };
    setCurrentUser(user);
    localStorage.setItem('currentUser', JSON.stringify(user));
  };

  const register = async (email: string, password: string) => {
    // Check if this email is already a mock user
    const mockUser = getMockUserByEmail(email);
    if (mockUser) {
      // For demo purposes, just log them in
      const user: User = {
        id: mockUser.userId,
        email: mockUser.email,
        displayName: mockUser.displayName
      };
      setCurrentUser(user);
      localStorage.setItem('currentUser', JSON.stringify(user));
      return;
    }
    
    // For new registrations, create new user
    const user: User = { 
      id: generateUserId(email),
      email, 
      displayName: email.split('@')[0] 
    };
    setCurrentUser(user);
    localStorage.setItem('currentUser', JSON.stringify(user));
  };

  const logout = async () => {
    setCurrentUser(null);
    localStorage.removeItem('currentUser');
  };

  const value = {
    currentUser,
    login,
    register,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
