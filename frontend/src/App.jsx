import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import IrrigationControl from './pages/IrrigationControl';
import ExplainableAI from './pages/ExplainableAI';
import CropAnalysis from './pages/CropAnalysis';
import { LiveData, Settings } from './pages/Placeholders';
import Login from './pages/Login';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Protected Route Wrapper
const PrivateRoute = ({ children }) => {
  const { currentUser } = useAuth();
  return currentUser ? children : <Navigate to="/login" />;
};

import AdminDashboard from './pages/AdminDashboard'; // Import

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route path="/*" element={
            <PrivateRoute>
              <Layout>
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/live-data" element={<LiveData />} />
                  <Route path="/analysis" element={<CropAnalysis />} />
                  <Route path="/irrigation" element={<IrrigationControl />} />
                  <Route path="/explainable-ai" element={<ExplainableAI />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="/admin" element={<AdminDashboard />} /> {/* New Route */}
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
