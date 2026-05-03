// src/pages/PreviewPage.jsx

import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const PreviewPage = () => {
  const { billId } = useParams();
  const navigate = useNavigate();

  // TODO: Fetch the specific bill data using the billId
  // For now, we'll just display the ID.

  return (
    <div>
      <h1>Preview Page</h1>
      <p>This page will show a preview of the details for Bill ID: <strong>{billId}</strong>.</p>
      <p>More functionality needs to be added here based on your requirements.</p>
      <button onClick={() => navigate('/')}>Back to Dashboard</button>
    </div>
  );
};

export default PreviewPage;