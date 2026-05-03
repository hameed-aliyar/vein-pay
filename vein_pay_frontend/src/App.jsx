// in src/App.jsx - FINAL REPLACEMENT CODE

import React from 'react';
import { BrowserRouter, Routes, Route, Outlet, Navigate } from 'react-router-dom';

// New Import
import ProtectedRoute from './components/ProtectedRoute'; 
import NavBar from './components/NavBar';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import NewBillPage from './pages/NewBillPage';
import NewCustomerPage from './pages/NewCustomerPage';
import PaymentOptionsPage from './pages/PaymentOptionsPage';
import PreviewPage from './pages/PreviewPage'; // Import the new preview page
import './App.css';

// Layout Component wraps content with the NavBar
const Layout = () => (
  <>
    <NavBar /> 
    <Outlet /> 
  </>
);

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Route: Login */}
        <Route path="/login" element={<LoginPage />} />
        
        {/* Protected Group: All main app pages */}
        <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          {/* Dashboard (Root path) */}
          <Route path="/" element={<DashboardPage />} /> 
          
          {/* Register Customer */}
          <Route path="/new-customer" element={<NewCustomerPage />} /> 
          
          {/* Generate Bill */}
          <Route path="/new-bill" element={<NewBillPage />} /> 
          
          {/* Payment Options */}
          <Route path="/pay/:billId" element={<PaymentOptionsPage />} />

          {/* NEW: Preview Page Route */}
          <Route path="/preview/:billId" element={<PreviewPage />} />
        </Route>
        
        {/* Fallback/404 Route: Redirects non-existent pages to the Dashboard */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;