/**
 * Login Page
 * Secure authentication entry point
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Shield, AlertCircle } from 'lucide-react';

export function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    console.log('🔐 [LoginPage] Login attempt started:', { username, passwordLength: password.length });

    try {
      console.log('🔐 [LoginPage] Calling login function...');
      await login({ username, password });
      console.log('✅ [LoginPage] Login successful! Navigating to dashboard...');
      
      // Navigate immediately - user state is now set
      navigate('/dashboard', { replace: true });
      console.log('🚀 [LoginPage] Navigation to dashboard triggered');
      
      // Keep loading state true during navigation
    } catch (err: any) {
      console.error('❌ [LoginPage] Login error:', err);
      console.error('❌ [LoginPage] Error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status
      });
      
      const errorMessage = err.response?.data?.detail 
        || err.message 
        || 'Invalid credentials. Please check your username and password.';
      
      setError(errorMessage);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-900 via-primary-800 to-primary-700">
      <div className="max-w-md w-full mx-4">
        <div className="bg-white rounded-lg shadow-2xl p-8">
          {/* Logo and Title */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
              <Shield className="w-8 h-8 text-primary-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">
              492-Energy-Defense
            </h1>
            <p className="text-gray-600 mt-2">
              Cybersecurity Defense System
            </p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="mb-6 p-4 bg-danger-50 border border-danger-200 rounded-lg flex items-start">
              <AlertCircle className="w-5 h-5 text-danger-600 mr-3 mt-0.5" />
              <div>
                <h3 className="font-semibold text-danger-800">
                  Authentication Failed
                </h3>
                <p className="text-sm text-danger-700 mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label
                htmlFor="username"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Username
              </label>
              <input
                id="username"
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                placeholder="Enter your username"
                autoComplete="username"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                placeholder="Enter your password"
                autoComplete="current-password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              {loading ? 'Authenticating...' : 'Sign In'}
            </button>
          </form>

          {/* Demo Credentials */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">
              Demo Credentials:
            </h3>
            <div className="space-y-3 text-sm">
              <div className="bg-primary-50 rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-primary-900">Admin Account</span>
                  <span className="text-xs text-primary-700">Full Access</span>
                </div>
                <div className="font-mono text-xs text-primary-800">
                  <div>Username: <span className="font-bold">admin</span></div>
                  <div>Password: <span className="font-bold">admin123</span></div>
                </div>
              </div>
              <div className="bg-blue-50 rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-blue-900">Analyst Account</span>
                  <span className="text-xs text-blue-700">View & Edit</span>
                </div>
                <div className="font-mono text-xs text-blue-800">
                  <div>Username: <span className="font-bold">analyst</span></div>
                  <div>Password: <span className="font-bold">admin123</span></div>
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-gray-900">Observer Account</span>
                  <span className="text-xs text-gray-700">Read Only</span>
                </div>
                <div className="font-mono text-xs text-gray-800">
                  <div>Username: <span className="font-bold">observer</span></div>
                  <div>Password: <span className="font-bold">admin123</span></div>
                </div>
              </div>
            </div>
            <p className="mt-3 text-xs text-gray-500 text-center italic">
              Note: Usernames are case-insensitive
            </p>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-white text-sm mt-6">
          Energy Sector Cybersecurity Defense System v1.0
        </p>
      </div>
    </div>
  );
}
