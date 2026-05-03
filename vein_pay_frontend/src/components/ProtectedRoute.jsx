// src/components/ProtectedRoute.jsx

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
    // Check for the presence of the access token
    const isAuthenticated = localStorage.getItem('access_token');
    const location = useLocation();

    if (!isAuthenticated) {
        // Redirect to the login page, saving the original location
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    // If authenticated, render the child components (Dashboard, Forms, etc.)
    return children;
};

export default ProtectedRoute;