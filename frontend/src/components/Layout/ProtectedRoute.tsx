'use client';

import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { ReactNode, useEffect } from 'react';

interface ProtectedRouteProps {
  children: ReactNode;
  fallbackRedirect?: string;
}

const ProtectedRoute = ({
  children,
  fallbackRedirect = '/login'
}: ProtectedRouteProps) => {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push(fallbackRedirect);
    }
  }, [isAuthenticated, isLoading, router, fallbackRedirect]);

  // Listen for unauthorized events
  useEffect(() => {
    const handleUnauthorized = () => {
      router.push('/login');
    };

    window.addEventListener('unauthorized', handleUnauthorized);

    return () => {
      window.removeEventListener('unauthorized', handleUnauthorized);
    };
  }, [router]);

  // Show nothing while checking authentication status
  if (isLoading) {
    return <div>Loading...</div>;
  }

  // Redirect happens via useEffect, but return children if authenticated
  if (isAuthenticated) {
    return <>{children}</>;
  }

  // If not authenticated, return nothing (redirect happens via useEffect)
  return null;
};

export default ProtectedRoute;