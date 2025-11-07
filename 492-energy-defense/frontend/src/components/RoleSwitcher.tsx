/**
 * Role Switcher Component
 * Allows quick switching between admin/analyst/observer views
 */
import React from 'react';
import { useAuth } from '@/context/AuthContext';
import { Shield, Eye, Activity } from 'lucide-react';
import type { UserRole } from '@/types';

export function RoleSwitcher() {
  const { currentRole, switchRole } = useAuth();

  const roles: { value: UserRole; label: string; icon: React.ReactNode; color: string; description: string }[] = [
    {
      value: 'admin',
      label: 'Admin',
      icon: <Shield className="w-4 h-4" />,
      color: 'bg-red-500 hover:bg-red-600',
      description: 'Full system access',
    },
    {
      value: 'analyst',
      label: 'Analyst',
      icon: <Activity className="w-4 h-4" />,
      color: 'bg-blue-500 hover:bg-blue-600',
      description: 'Analysis & feedback',
    },
    {
      value: 'observer',
      label: 'Observer',
      icon: <Eye className="w-4 h-4" />,
      color: 'bg-green-500 hover:bg-green-600',
      description: 'Read-only access',
    },
  ];

  return (
    <div className="flex items-center gap-2 bg-gray-800 rounded-lg p-1">
      {roles.map((role) => (
        <button
          key={role.value}
          onClick={() => switchRole(role.value)}
          className={`
            flex items-center gap-2 px-3 py-2 rounded-md transition-all
            ${
              currentRole === role.value
                ? `${role.color} text-white shadow-lg`
                : 'text-gray-400 hover:text-white hover:bg-gray-700'
            }
          `}
          title={role.description}
        >
          {role.icon}
          <span className="text-sm font-medium">{role.label}</span>
        </button>
      ))}
    </div>
  );
}
