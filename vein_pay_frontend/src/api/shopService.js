import api from './api';

export const getBills = async () => {
  try {
    const response = await api.get('/shop/bills/');
    return response.data;
  } catch (error) {
    console.error("Failed to fetch bills:", error);
    throw error;
  }
};

export const getCustomers = async () => {
  try {
    const response = await api.get('/shop/customers/');
    return response.data;
  } catch (error) {
    console.error("Failed to fetch customers:", error);
    throw error;
  }
};

export const createBill = async (billData) => {
  try {
    const response = await api.post('/shop/bills/', billData); // JSON is fine
    return response.data;
  } catch (error) {
    console.error("Failed to create bill:", error.response?.data || error);
    throw error;
  }
};

export const createCustomer = async (customerData) => {
  try {
    const formData = new FormData();

    formData.append("username", customerData.username.trim());
    formData.append("password", customerData.password);
    formData.append("biometric_type", "VEIN");

    if (customerData.veinImage) {
      formData.append("vein_image", customerData.veinImage);
    }

    // DEBUG (VERY IMPORTANT)
    for (let [key, value] of formData.entries()) {
      console.log("📦", key, value);
    }

    const response = await api.post("/shop/customers/", formData);

    return response.data;

  } catch (error) {
    console.error("❌ CREATE CUSTOMER FAILED:");
    console.log("Status:", error.response?.status);
    console.log("Data:", error.response?.data);

    throw error;
  }
};

export const payBillWithVein = async (billId, veinImage) => {
  try {
    const formData = new FormData();
    formData.append('bill_id', billId);
    formData.append('live_image', veinImage, 'vein_image.jpg');

    const token = localStorage.getItem('access_token');
    if (!token) throw new Error("Authentication token not found.");

    const config = { headers: { 'Authorization': `Bearer ${token}` } };
    const response = await api.post('/pay/', formData, config);
    return response.data;
  } catch (error) {
    console.error("Failed to process vein payment:", error);
    throw error;
  }
};

export const payBillWithCash = async (billId) => {
  try {
    const response = await api.put(`/shop/bills/${billId}/pay-cash/`);
    return response.data;
  } catch (error) {
    console.error("Failed to mark bill as paid in cash:", error);
    throw error;
  }
};

// in src/api/shopService.js

export const payBillWithFace = async (billId, liveImage) => {
  try {
    const formData = new FormData();
    formData.append('bill_id', billId);
    formData.append('live_image', liveImage, 'live_image.jpg');

    // --- FORCEFUL FIX ---
    // Manually get the token from localStorage
    const token = localStorage.getItem('access_token');
    if (!token) {
      // This is a safeguard in case the user is not logged in
      throw new Error("Authentication token not found.");
    }

    // Create a config object and manually add the Authorization header
    const config = {
      headers: {
        'Authorization': `Bearer ${token}`,
        // We do NOT set 'Content-Type'. Axios will do it automatically for FormData.
      }
    };
    
    // Pass the custom config with the token as the third argument
    const response = await api.post('/pay/', formData, config);
    return response.data;
    
  } catch (error)    {
    console.error("Failed to process biometric payment:", error);
    throw error;
  }
};