import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getBills, getCustomers, payBillWithCash } from '../api/shopService';
import PaymentModal from '../components/PaymentModal';

const DashboardPage = () => {
  const [bills, setBills] = useState([]);
  const [customerMap, setCustomerMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [billForPayment, setBillForPayment] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [billsData, customersData] = await Promise.all([getBills(), getCustomers()]);
      const customers = customersData.reduce((acc, customer) => {
        acc[customer.id] = customer.username;
        return acc;
      }, {});
      setBills(billsData);
      setCustomerMap(customers);
    } catch (err) {
      setError('Failed to load dashboard data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handlePayCash = async (billId) => {
    if (window.confirm('Are you sure you want to mark this bill as paid in cash?')) {
      try {
        await payBillWithCash(billId);
        fetchData(); // Refresh the bill list
      } catch (err) {
        alert('Failed to process cash payment.');
      }
    }
  };

  if (loading) return <div>Loading dashboard...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  if (billForPayment) {
    return (
      <PaymentModal
        bill={billForPayment}
        customerName={customerMap[billForPayment.customer]}
        onClose={() => setBillForPayment(null)}
        onPaymentSuccess={() => {
          setBillForPayment(null);
          fetchData();
        }}
      />
    );
  }

  return (
    <div>
      <h1>Dashboard</h1>
      <div style={{ margin: '20px 0' }}>
        <Link to="/new-bill"><button>+ Add New Bill</button></Link>
        <Link to="/new-customer" style={{ marginLeft: '10px' }}><button>+ Add New Customer</button></Link>
      </div>
      <h2>Bills</h2>
      <table>
        <thead>
          <tr>
            <th>Bill ID</th>
            <th>Customer</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
            {bills.map((bill) => (
                <tr key={bill.id}>
                <td>{bill.id}</td>
                <td>{customerMap[bill.customer] || `ID: ${bill.customer}`}</td>
                <td>₹{bill.amount}</td>
                <td>{bill.status}</td>
                <td>
                    {/*
                    THIS IS THE NEW, MORE ROBUST CHECK.
                    It converts the status to lowercase before comparing,
                    so it will work for "Pending", "pending", etc.
                    */}
                    {bill.status && bill.status.toLowerCase() === 'pending' && (
                    <Link to={`/pay/${bill.id}`} state={{ bill, customerName: customerMap[bill.customer] }}>
                        <button>Pay Bill</button>
                    </Link>
                    )}
                </td>
                </tr>
            ))}
        </tbody>
      </table>
    </div>
  );
};

export default DashboardPage;