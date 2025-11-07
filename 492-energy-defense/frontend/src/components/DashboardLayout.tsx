/**
 * Dashboard Layout - Demo Mode
 * Main application shell with role switcher
 */
import React, { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { RoleSwitcher } from '@/components/RoleSwitcher';
import {
  Shield,
  LayoutDashboard,
  AlertTriangle,
  Settings,
  User,
  MessageSquare,
} from 'lucide-react';
import clsx from 'clsx';

interface DashboardLayoutProps {
  children: ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const { user, hasRole } = useAuth();
  const location = useLocation();

  const menuItems = [
    {
      name: 'Dashboard',
      path: '/dashboard',
      icon: LayoutDashboard,
      roles: ['admin', 'analyst', 'observer'],
    },
    {
      name: 'Vulnerabilities',
      path: '/vulnerabilities',
      icon: AlertTriangle,
      roles: ['admin', 'analyst', 'observer'],
    },
    {
      name: 'AI Configuration',
      path: '/ai-config',
      icon: Settings,
      roles: ['admin'],
    },
    {
      name: 'Feedback',
      path: '/feedback',
      icon: MessageSquare,
      roles: ['admin', 'analyst'],
    },
  ];

  const canAccessItem = (itemRoles: string[]) => {
    return hasRole(itemRoles as any);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Shield className="w-8 h-8 text-primary-600" />
              <div className="ml-3">
                <div className="text-xl font-bold text-gray-900">
                  492-Energy-Defense
                </div>
                <div className="text-xs text-gray-500">Demo Mode</div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Role Switcher */}
              <RoleSwitcher />

              {/* Current User Info */}
              <div className="flex items-center space-x-2 border-l border-gray-200 pl-4">
                <User className="w-5 h-5 text-gray-500" />
                <div className="text-sm">
                  <div className="font-medium text-gray-900">
                    {user.username}
                  </div>
                  <div className="text-gray-500 capitalize text-xs">{user.role}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-white shadow-sm min-h-[calc(100vh-4rem)]">
          <nav className="p-4 space-y-2">
            {menuItems
              .filter((item) => canAccessItem(item.roles))
              .map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;

                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={clsx(
                      'flex items-center px-4 py-3 text-sm font-medium rounded-lg transition',
                      isActive
                        ? 'bg-primary-50 text-primary-700 border border-primary-200'
                        : 'text-gray-700 hover:bg-gray-100'
                    )}
                  >
                    <Icon className="w-5 h-5 mr-3" />
                    {item.name}
                  </Link>
                );
              })}
          </nav>

          {/* Role Badge */}
          <div className="p-4 border-t border-gray-200 mt-4">
            <div
              className={clsx(
                'px-3 py-2 rounded-lg text-sm font-semibold text-center',
                user.role === 'admin' &&
                  'bg-red-100 text-red-700 border border-red-200',
                user.role === 'analyst' &&
                  'bg-blue-100 text-blue-700 border border-blue-200',
                user.role === 'observer' &&
                  'bg-green-100 text-green-700 border border-green-200'
              )}
            >
              {user.role.toUpperCase()} ACCESS
            </div>
            <div className="mt-2 text-xs text-gray-500 text-center">
              Switch roles using the buttons above
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-8">{children}</main>
      </div>
    </div>
  );
}
