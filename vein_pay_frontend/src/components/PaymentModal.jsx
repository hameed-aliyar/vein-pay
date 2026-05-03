import React, { useState } from 'react';
import { payBillWithVein } from '../api/shopService';

const PaymentModal = ({ bill, customerName, onClose, onPaymentSuccess }) => {
  const [veinImage, setVeinImage] = useState(null);
  const [error, setError] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const handleConfirmPayment = async () => {
    if (!veinImage) {
      setError('Please upload a vein image first.');
      return;
    }
    setIsProcessing(true);
    setError('');
    try {
      await payBillWithVein(bill.id, veinImage);
      alert('Payment successful!');
      onPaymentSuccess();
    } catch (err) {
      setError('Vein biometric payment failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div style={styles.overlay}>
      <div style={styles.modal}>
        <h2>Vein Biometric Payment</h2>
        <p>Confirming payment of ₹{bill.amount} for {customerName}</p>

        <div>
          <label>Upload Vein Image:</label>
          <input type="file" accept="image/*" onChange={(e) => setVeinImage(e.target.files[0])} />
        </div>

        {error && <p style={{ color: 'red' }}>{error}</p>}

        <div style={{ marginTop: '20px' }}>
          <button onClick={onClose} disabled={isProcessing}>Cancel</button>
          <button onClick={handleConfirmPayment} disabled={!veinImage || isProcessing} style={{ marginLeft: '10px' }}>
            {isProcessing ? 'Processing...' : 'Confirm Payment'}
          </button>
        </div>
      </div>
    </div>
  );
};

const styles = {
  overlay: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center' },
  modal: { backgroundColor: '#fff', padding: '20px', borderRadius: '8px', width: '400px' },
};

export default PaymentModal;