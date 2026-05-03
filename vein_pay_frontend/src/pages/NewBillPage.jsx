import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCustomers, createBill } from '../api/shopService';

const NewBillPage = () => {
  const [customers, setCustomers] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState('');
  const [amount, setAmount] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    getCustomers()
      .then((data) => {
        console.log("Fetched customers:", data); // <- debug
        setCustomers(data);
      })
      .catch(() => {
        setError('Could not load customers.');
      });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!selectedCustomer || !amount) {
      setError('Please select a customer and enter an amount.');
      return;
    }

    const customerId = Number(selectedCustomer);
    if (!customerId) {
      setError('Please select a valid customer.');
      return;
    }

    const billData = {
      customer: customerId,
      amount: parseFloat(amount).toFixed(2),
    };

    console.log('Submitting bill data:', billData);

    try {
      await createBill(billData);
      navigate('/');
    } catch (err) {
      console.error('Create bill error:', err);
      setError('Failed to create the bill. Check console for details.');
    }
  };

  // <-- return MUST be inside the component function
  return (
    <div>
      <h1>Create New Bill</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="customer">Customer</label>
          <select
            id="customer"
            value={selectedCustomer}
            onChange={(e) => setSelectedCustomer(e.target.value)}
            required
          >
            <option value="">Select a customer</option>
            {customers.map((customer) => (
              <option key={customer.id} value={customer.id}>
                {customer.username}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="amount">Amount (₹)</label>
          <input
            type="number"
            id="amount"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            required
          />
        </div>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <button type="submit">Create Bill</button>
      </form>
    </div>
  );
};

export default NewBillPage;