import React, { useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { payBillWithCash } from '../api/shopService';
import PaymentModal from '../components/PaymentModal';

const PaymentOptionsPage = () => {
  const { billId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  
  const { bill, customerName } = location.state || {};
  
  const [showWalletPay, setShowWalletPay] = useState(false);

  if (!bill) {
    return <div>Error: Bill data not found. Please go back to the dashboard.</div>;
  }
  
  const handlePayCash = async () => {
    if (window.confirm('Are you sure you want to mark this bill as paid in cash?')) {
      try {
        await payBillWithCash(billId);
        alert('Payment successful!');
        navigate('/');
      } catch (err) {
        alert('Failed to process cash payment.');
      }
    }
  };

  if (showWalletPay) {
    return (
      <PaymentModal
        bill={bill}
        customerName={customerName}
        onClose={() => setShowWalletPay(false)}
        onPaymentSuccess={() => {
          setShowWalletPay(false);
          navigate('/');
        }}
      />
    );
  }

  return (
    <div>
      <h1>Process Payment for Bill #{billId}</h1>
      <h2>Amount: ₹{bill.amount}</h2>
      <h3>Customer: {customerName}</h3>
      <hr />
      <div style={{ marginTop: '20px' }}>
        <button onClick={handlePayCash}>Pay with Cash</button>
        <button onClick={() => setShowWalletPay(true)} style={{ marginLeft: '10px' }}>
          Pay with Wallet (Face/Vein)
        </button>
      </div>
      <button onClick={() => navigate('/')} style={{ marginTop: '20px' }}>Back to Dashboard</button>
    </div>
  );
};

export default PaymentOptionsPage;