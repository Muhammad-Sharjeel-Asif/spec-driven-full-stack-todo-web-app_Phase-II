'use client';

import { useContext } from 'react';
import { AuthContext, AuthContextType } from '@/providers/AuthProvider';

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Re-export the types for convenience
export type { AuthContextType } from '@/providers/AuthProvider';