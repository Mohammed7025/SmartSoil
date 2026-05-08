import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import ExplainableAI from './pages/ExplainableAI';
import CropAnalysis from './pages/CropAnalysis';
import AISoilIntelligence from './pages/AISoilIntelligence';
import { LiveData } from './pages/Placeholders';
import Settings from './pages/Settings';

import Login from './pages/Login';
import Signup from './pages/Signup';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Protected Route Wrapper for any logged in user
const PrivateRoute = ({ children }) => {
  const { currentUser } = useAuth();
  return currentUser ? children : <Navigate to="/login" />;
};

// Admin Only Route Wrapper
const AdminRoute = ({ children }) => {
  const { currentUser } = useAuth();
  if (!currentUser) return <Navigate to="/login" />;
  if (currentUser.role !== 'admin') return <Navigate to="/dashboard" />;
  return children;
};

import AdminDashboard from './pages/AdminDashboard';
import Advisor from './pages/Advisor';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          <Route path="/*" element={
            <PrivateRoute>
              <Layout>
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/live-data" element={<LiveData />} />
                  <Route path="/analysis" element={<CropAnalysis />} />
                  <Route path="/soil-intelligence" element={<AISoilIntelligence />} />
                  <Route path="/explainable-ai" element={<ExplainableAI />} />
                  <Route path="/advisor" element={<Advisor />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="/admin" element={
                    <AdminRoute>
                      <AdminDashboard />
                    </AdminRoute>
                  } />
                </Routes>
              </Layout>
            </PrivateRoute>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
