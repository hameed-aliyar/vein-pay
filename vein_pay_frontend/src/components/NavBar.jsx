import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api/api'; // Your Axios instance

// Utility function to handle user logout
const handleLogout = (navigate) => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  navigate('/login'); 
};

const NavBar = () => {
  const navigate = useNavigate();
  const isAuthenticated = localStorage.getItem('access_token');

  const [walletBalance, setWalletBalance] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch wallet balance
  const fetchWalletBalance = async () => {
    if (!isAuthenticated) return;

    setLoading(true);
    try {
      const response = await api.get('/wallet/');
      setWalletBalance(response.data.balance);
    } catch (err) {
      console.error('Failed to fetch wallet balance:', err);
      setWalletBalance(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWalletBalance();

    // Optional: refresh balance every 30s
    const interval = setInterval(fetchWalletBalance, 30000);
    return () => clearInterval(interval);
  }, [isAuthenticated]);

  return (
    <nav className="navbar">
      <div className="navbar-logo">VeinPAY</div>
      <div className="navbar-links">
        <Link to="/">Dashboard</Link>
        <Link to="/new-customer">Register Customer</Link>
        <Link to="/new-bill">Generate Bill</Link>

        {isAuthenticated && (
          <span style={{ marginLeft: '20px', fontWeight: 'bold' }}>
            Wallet: {loading ? 'Loading...' : walletBalance !== null ? `₹${walletBalance}` : 'N/A'}
          </span>
        )}

        {isAuthenticated ? (
          <button onClick={() => handleLogout(navigate)} style={{ marginLeft: '20px' }}>
            Logout
          </button>
        ) : (
          <Link to="/login" style={{ marginLeft: '20px' }}>Login</Link>
        )}
      </div>
    </nav>
  );
};

export default NavBar;