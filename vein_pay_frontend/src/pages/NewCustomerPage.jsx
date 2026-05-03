import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createCustomer } from '../api/shopService';

const NewCustomerPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [veinImage, setVeinImage] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!veinImage) {
      setError('Please upload a vein image before registering.');
      return;
    }
    try {
      await createCustomer({ username, password, veinImage });
      navigate('/');
    } catch (err) {
      setError('Failed to create customer.');
    }
  };

  return (
    <div>
      <h1>Register New Customer</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Username</label>
          <input value={username} onChange={(e) => setUsername(e.target.value)} required />
        </div>
        <div>
          <label>Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </div>
        <div>
          <label>Upload Vein Image</label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setVeinImage(e.target.files[0])}
            required
          />
        </div>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <button type="submit">Register Customer</button>
      </form>
    </div>
  );
};

export default NewCustomerPage;