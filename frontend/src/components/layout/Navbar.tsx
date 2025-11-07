// Navigation bar component
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

export function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-dark-900 border-b border-dark-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <Link to="/dashboard" className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xl">ED</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Energy Defense</h1>
            <p className="text-xs text-gray-400">Cybersecurity Operations</p>
          </div>
        </Link>

        <div className="flex items-center space-x-6">
          <div className="text-right">
            <p className="text-sm font-medium text-white">{user?.username}</p>
            <p className="text-xs text-gray-400 capitalize">{user?.role}</p>
          </div>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-danger-600 hover:bg-danger-700 text-white text-sm font-medium rounded-lg transition duration-200"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
