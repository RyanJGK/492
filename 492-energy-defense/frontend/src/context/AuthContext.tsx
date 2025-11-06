/**
 * Authentication Context
 * Manages user authentication state and provides RBAC utilities
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '@/services/api';
import type { User, LoginCredentials, UserRole } from '@/types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  hasRole: (roles: UserRole[]) => boolean;
  isAdmin: boolean;
  isAnalyst: boolean;
  isObserver: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already authenticated
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const currentUser = await apiClient.getCurrentUser();
          setUser(currentUser);
        } catch (error) {
          console.error('Failed to fetch user:', error);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      // Login and get tokens
      await apiClient.login(credentials);
      
      // Fetch current user data
      const currentUser = await apiClient.getCurrentUser();
      setUser(currentUser);
      
      console.log('Login successful, user:', currentUser.username, 'role:', currentUser.role);
    } catch (error) {
      console.error('Login failed:', error);
      // Clear any partial state
      setUser(null);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      throw error;
    }
  };

  const logout = async () => {
    await apiClient.logout();
    setUser(null);
  };

  const hasRole = (roles: UserRole[]): boolean => {
    if (!user) return false;
    return roles.includes(user.role);
  };

  const value: AuthContextType = {
    user,
    loading,
    login,
    logout,
    hasRole,
    isAdmin: user?.role === 'admin',
    isAnalyst: user?.role === 'analyst' || user?.role === 'admin',
    isObserver: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

/**
 * HOC for role-based route protection
 */
export function RequireRole({
  children,
  roles,
}: {
  children: ReactNode;
  roles: UserRole[];
}) {
  const { user, hasRole } = useAuth();

  if (!user) {
    return <div>Please log in to access this page.</div>;
  }

  if (!hasRole(roles)) {
    return (
      <div className="p-8 text-center">
        <h2 className="text-2xl font-bold text-danger-600">Access Denied</h2>
        <p className="mt-4 text-gray-600">
          You do not have permission to access this page.
        </p>
        <p className="mt-2 text-sm text-gray-500">
          Required role(s): {roles.join(', ')}
        </p>
      </div>
    );
  }

  return <>{children}</>;
}
