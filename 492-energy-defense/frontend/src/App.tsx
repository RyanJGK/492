/**
 * Main Application Component
 * Demo mode - no authentication required
 */
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/context/AuthContext';
import { DashboardLayout } from '@/components/DashboardLayout';
import { DashboardPage } from '@/pages/DashboardPage';
import { VulnerabilitiesPage } from '@/pages/VulnerabilitiesPage';
import { AIConfigPage } from '@/pages/AIConfigPage';
import { FeedbackPage } from '@/pages/FeedbackPage';

/**
 * Main App Component - Demo Mode
 * All routes are accessible, role switching handled in dashboard
 */
function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* All routes wrapped in dashboard layout */}
          <Route
            path="/dashboard"
            element={
              <DashboardLayout>
                <DashboardPage />
              </DashboardLayout>
            }
          />
          <Route
            path="/vulnerabilities"
            element={
              <DashboardLayout>
                <VulnerabilitiesPage />
              </DashboardLayout>
            }
          />
          <Route
            path="/ai-config"
            element={
              <DashboardLayout>
                <AIConfigPage />
              </DashboardLayout>
            }
          />
          <Route
            path="/feedback"
            element={
              <DashboardLayout>
                <FeedbackPage />
              </DashboardLayout>
            }
          />

          {/* Default Redirect */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
