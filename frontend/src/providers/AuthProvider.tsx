'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, AuthUser } from '@/types/user';
import { apiClient } from '@/lib/api-client';

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing session on mount
    // In a real implementation with httpOnly cookies, we would make an API call to verify the session
    // For now, we'll check localStorage but in production, httpOnly cookies would be preferred
    const verifySession = async () => {
      try {
        // Attempt to verify the session with the backend
        const userData = await apiClient.getCurrentUser();
        setUser(userData.data);
        setToken('session-active'); // Token is managed by httpOnly cookies in the backend
      } catch (error) {
        // Session is not valid, clear any local data
        console.log('No valid session found');
      }
      setIsLoading(false);
    };

    verifySession();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      // The API call will set httpOnly cookies for the JWT token
      const response = await apiClient.login({ email, password });
      const userData = response.data.user; // Adjust based on actual API response structure

      // Update local state with user data
      setUser(userData);
      setToken('session-active'); // Token is managed by httpOnly cookies in the backend
    } catch (error) {
      throw error;
    }
  };

  const register = async (name: string, email: string, password: string) => {
    try {
      // The API call will set httpOnly cookies for the JWT token
      const response = await apiClient.register({ name, email, password });
      const userData = response.data.user; // Adjust based on actual API response structure

      // Update local state with user data
      setUser(userData);
      setToken('session-active'); // Token is managed by httpOnly cookies in the backend
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    // Call API to clear httpOnly cookie session
    apiClient.logout()
      .catch(error => console.error('Logout API call failed:', error));

    // Clear local state
    setToken(null);
    setUser(null);
  };

  const refreshToken = async (): Promise<boolean> => {
    // Implement token refresh logic if needed
    // This is a simplified version - in practice, you'd make an API call to refresh the token
    return true;
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    refreshToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

