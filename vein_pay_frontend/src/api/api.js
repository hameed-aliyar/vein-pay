import axios from 'axios';

// Create a new Axios instance with a custom configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
});

// Use an interceptor to add the auth token to every request
api.interceptors.request.use(
  (config) => {
    // Get the token from localStorage (we'll save it there after login)
    const token = localStorage.getItem('access_token');
    if (token) {
      // If the token exists, add it to the Authorization header
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    // Do something with request error
    return Promise.reject(error);
  }
);

export default api;