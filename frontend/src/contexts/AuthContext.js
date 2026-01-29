import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../services/api';

// Create the Auth Context
const AuthContext = createContext();

// Provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(null);

  // Check if user is already logged in on initial load
  useEffect(() => {
    const token = localStorage.getItem('jwt_token');
    if (token) {
      setToken(token);
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, []);

  // Fetch current user details
  const fetchCurrentUser = async () => {
    try {
      const userData = await authApi.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      logout(); // Clear token if it's invalid
    } finally {
      setLoading(false);
    }
  };

  // Login function
  const login = async (credentials) => {
    try {
      const response = await authApi.login(credentials);

      // Store token in localStorage
      const jwtToken = response.access_token || response.token;
      if (jwtToken) {
        localStorage.setItem('jwt_token', jwtToken);
        setToken(jwtToken);

        // Set token in API client
        // Assuming there's a way to set the token in your API client
        // This may vary depending on how your API client is implemented
      }

      // Set user data
      setUser(response.user || response);

      return { success: true, user: response.user || response };
    } catch (error) {
      console.error('Login failed:', error);
      return { success: false, error: error.message || 'Login failed' };
    }
  };

  // Register function
  const register = async (userData) => {
    try {
      const response = await authApi.register(userData);

      // Store token in localStorage if returned
      if (response.access_token) {
        localStorage.setItem('jwt_token', response.access_token);
        setToken(response.access_token);
      }

      setUser(response.user || response);

      return { success: true, user: response.user || response };
    } catch (error) {
      console.error('Registration failed:', error);
      return { success: false, error: error.message || 'Registration failed' };
    }
  };

  // Logout function
  const logout = () => {
    // Remove token from localStorage
    localStorage.removeItem('jwt_token');

    // Clear token state
    setToken(null);

    // Clear user state
    setUser(null);

    // Clear token in API client if needed
    // This may vary depending on how your API client handles authentication
  };

  // Check if user is authenticated
  const isAuthenticated = !!user;

  // Listen for unauthorized events to automatically logout
  useEffect(() => {
    const handleUnauthorized = () => {
      logout();
    };

    const handleForbidden = () => {
      // Could handle forbidden access differently if needed
      console.warn('Forbidden access attempted');
    };

    window.addEventListener('unauthorized', handleUnauthorized);
    window.addEventListener('forbidden', handleForbidden);

    // Cleanup event listeners
    return () => {
      window.removeEventListener('unauthorized', handleUnauthorized);
      window.removeEventListener('forbidden', handleForbidden);
    };
  }, []);

  // Value to be provided to consumers
  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    isAuthenticated,
    fetchCurrentUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the Auth Context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;