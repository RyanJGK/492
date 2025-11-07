// Authentication context and hook
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '../services/api';
import type { User, AuthToken } from '../types';

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem('access_token');
    if (token) {
      // Decode JWT to get user info (simplified - in production use proper JWT library)
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setUser({
          id: 0,
          username: payload.sub,
          email: '',
          role: payload.role,
          is_active: true,
          created_at: '',
        });
      } catch (error) {
        console.error('Failed to parse token:', error);
        localStorage.removeItem('access_token');
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const tokens = await apiClient.login(username, password);
      localStorage.setItem('access_token', tokens.access_token);
      localStorage.setItem('refresh_token', tokens.refresh_token);

      // Decode token to get user info
      const payload = JSON.parse(atob(tokens.access_token.split('.')[1]));
      setUser({
        id: 0,
        username: payload.sub,
        email: '',
        role: payload.role,
        is_active: true,
        created_at: '',
      });
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        isAuthenticated: !!user,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export function useRBAC(allowedRoles: string[]) {
  const { user } = useAuth();
  return user && allowedRoles.includes(user.role);
}
