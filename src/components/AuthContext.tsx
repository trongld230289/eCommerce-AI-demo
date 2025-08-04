import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { mockUserList } from '../utils/mockUserList';

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
	const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedUser = localStorage.getItem('currentUser');
    if (storedUser) {
      setCurrentUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

	useEffect(() => {
    if (currentUser) {
      localStorage.setItem('currentUser', JSON.stringify(currentUser));
    } else {
      localStorage.removeItem('currentUser');
    }

    console.log("🔹 currentUser in localStorage:", localStorage.getItem('currentUser'));
  }, [currentUser]);

	useEffect(() => {
    if (currentUser) {
      localStorage.setItem('currentUser', JSON.stringify(currentUser));
    } else {
      localStorage.removeItem('currentUser');
    }

    console.log("🔹 currentUser in localStorage:", localStorage.getItem('currentUser'));
  }, [currentUser]);

  const login = async (email: string, password: string) => {
    const user = mockUserList.find(
      (u) => u.email.toLowerCase() === email.toLowerCase() && u.password === password
    );

    if (!user) {
      throw new Error('Invalid email or password');
    }
    setCurrentUser({ email: user.email, displayName: user.displayName });
  };

  const register = async (email: string, password: string) => {
    const displayName = email.split('@')[0];
    const newUser = { email, displayName };
    setCurrentUser(newUser);
    localStorage.setItem('currentUser', JSON.stringify(newUser));
		console.log(currentUser);
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
       {!loading && children}
    </AuthContext.Provider>
  );
};
