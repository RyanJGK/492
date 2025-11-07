// Main App component with routing
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './hooks/useAuth';
import { LoginForm } from './components/auth/LoginForm';
import { Navbar } from './components/layout/Navbar';
import { Sidebar } from './components/layout/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { AuthEvents } from './pages/AuthEvents';
import { NetworkAnalysis } from './pages/NetworkAnalysis';
import { Vulnerabilities } from './pages/Vulnerabilities';
import { AIInsights } from './pages/AIInsights';
import { AdminConfig } from './pages/AdminConfig';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function PrivateRoute({ children, allowedRoles }: { children: React.ReactNode; allowedRoles?: string[] }) {
  const { isAuthenticated, user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-dark-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" />;
  }

  return <>{children}</>;
}

function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-dark-900">
      <Navbar />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-8">{children}</main>
      </div>
    </div>
  );
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginForm />} />
      
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <AppLayout>
              <Dashboard />
            </AppLayout>
          </PrivateRoute>
        }
      />
      
      <Route
        path="/auth-events"
        element={
          <PrivateRoute>
            <AppLayout>
              <AuthEvents />
            </AppLayout>
          </PrivateRoute>
        }
      />
      
      <Route
        path="/network"
        element={
          <PrivateRoute>
            <AppLayout>
              <NetworkAnalysis />
            </AppLayout>
          </PrivateRoute>
        }
      />
      
      <Route
        path="/vulnerabilities"
        element={
          <PrivateRoute>
            <AppLayout>
              <Vulnerabilities />
            </AppLayout>
          </PrivateRoute>
        }
      />
      
      <Route
        path="/ai-insights"
        element={
          <PrivateRoute>
            <AppLayout>
              <AIInsights />
            </AppLayout>
          </PrivateRoute>
        }
      />
      
      <Route
        path="/admin"
        element={
          <PrivateRoute allowedRoles={['admin']}>
            <AppLayout>
              <AdminConfig />
            </AppLayout>
          </PrivateRoute>
        }
      />
      
      <Route path="/" element={<Navigate to="/dashboard" />} />
    </Routes>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
