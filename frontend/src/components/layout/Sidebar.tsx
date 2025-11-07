// Sidebar navigation component
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth, useRBAC } from '../../hooks/useAuth';

interface NavItem {
  path: string;
  label: string;
  roles: string[];
}

const navItems: NavItem[] = [
  { path: '/dashboard', label: 'Dashboard', roles: ['admin', 'analyst', 'observer'] },
  { path: '/auth-events', label: 'Authentication', roles: ['admin', 'analyst', 'observer'] },
  { path: '/network', label: 'Network Traffic', roles: ['admin', 'analyst', 'observer'] },
  { path: '/vulnerabilities', label: 'Vulnerabilities', roles: ['admin', 'analyst', 'observer'] },
  { path: '/ai-insights', label: 'AI Insights', roles: ['admin', 'analyst', 'observer'] },
  { path: '/admin', label: 'Configuration', roles: ['admin'] },
];

export function Sidebar() {
  const location = useLocation();
  const { user } = useAuth();

  const filteredItems = navItems.filter((item) =>
    user && item.roles.includes(user.role)
  );

  return (
    <aside className="w-64 bg-dark-800 border-r border-dark-700 min-h-screen p-6">
      <nav className="space-y-2">
        {filteredItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`block px-4 py-3 rounded-lg transition duration-200 ${
                isActive
                  ? 'bg-primary-600 text-white font-medium'
                  : 'text-gray-300 hover:bg-dark-700 hover:text-white'
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
