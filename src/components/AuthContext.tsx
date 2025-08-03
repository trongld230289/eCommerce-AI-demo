import React, { createContext, useContext, useState, ReactNode } from 'react';

interface User {
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

  const login = async (email: string, password: string) => {
    // Simple mock login
    setCurrentUser({ email, displayName: email.split('@')[0] });
  };

  const register = async (email: string, password: string) => {
    // Simple mock register
    setCurrentUser({ email, displayName: email.split('@')[0] });
  };

  const logout = async () => {
    setCurrentUser(null);
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
