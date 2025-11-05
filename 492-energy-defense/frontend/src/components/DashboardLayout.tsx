/**
 * Dashboard Layout
 * Main application shell with navigation and role-based menu
 */
import React, { ReactNode } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import {
  Shield,
  LayoutDashboard,
  AlertTriangle,
  Settings,
  LogOut,
  User,
  MessageSquare,
} from 'lucide-react';
import clsx from 'clsx';

interface DashboardLayoutProps {
  children: ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const { user, logout, isAdmin, isAnalyst } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

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
    return user && itemRoles.includes(user.role);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Shield className="w-8 h-8 text-primary-600" />
              <span className="ml-3 text-xl font-bold text-gray-900">
                492-Energy-Defense
              </span>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <User className="w-5 h-5 text-gray-500" />
                <div className="text-sm">
                  <div className="font-medium text-gray-900">
                    {user?.username}
                  </div>
                  <div className="text-gray-500 capitalize">{user?.role}</div>
                </div>
              </div>

              <button
                onClick={handleLogout}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </button>
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
                user?.role === 'admin' &&
                  'bg-danger-100 text-danger-700 border border-danger-200',
                user?.role === 'analyst' &&
                  'bg-warning-100 text-warning-700 border border-warning-200',
                user?.role === 'observer' &&
                  'bg-success-100 text-success-700 border border-success-200'
              )}
            >
              {user?.role.toUpperCase()} ACCESS
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-8">{children}</main>
      </div>
    </div>
  );
}
