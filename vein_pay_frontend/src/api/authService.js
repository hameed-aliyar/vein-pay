import api from './api'; // Our configured Axios instance

export const login = async (username, password) => {
  try {
    const response = await api.post('/auth/login/', {
      username: username,
      password: password,
    });
    // Return the tokens from the response
    return response.data;
  } catch (error) {
    // Handle or throw the error
    console.error("Login failed:", error);
    throw error;
  }
};