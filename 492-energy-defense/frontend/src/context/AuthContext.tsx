/**
 * Auth Context - Simplified for Demo Mode
 * Allows toggling between user roles without authentication
 */
import React, { createContext, useContext, useState, useEffect } from 'react';
import type { User, UserRole } from '@/types';

interface AuthContextType {
  user: User;
  currentRole: UserRole;
  switchRole: (role: UserRole) => void;
  hasRole: (roles: UserRole[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [currentRole, setCurrentRole] = useState<UserRole>(() => {
    // Load from localStorage or default to admin
    const savedRole = localStorage.getItem('demo_role');
    return (savedRole as UserRole) || 'admin';
  });

  // Create a demo user based on current role
  const user: User = {
    id: currentRole === 'admin' ? 1 : currentRole === 'analyst' ? 2 : 3,
    username: currentRole,
    email: `${currentRole}@energy-defense.local`,
    role: currentRole,
    is_active: true,
    created_at: new Date().toISOString(),
    last_login: new Date().toISOString(),
  };

  const switchRole = (role: UserRole) => {
    console.log(`🔄 Switching role from ${currentRole} to ${role}`);
    setCurrentRole(role);
    localStorage.setItem('demo_role', role);
  };

  const hasRole = (roles: UserRole[]): boolean => {
    return roles.includes(currentRole);
  };

  const value: AuthContextType = {
    user,
    currentRole,
    switchRole,
    hasRole,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
