'use client';

import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    try {
      logout();
      router.push('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <nav className="bg-indigo-700 text-white shadow-md" role="navigation" aria-label="Main navigation">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="text-xl font-bold" aria-label="Taskify homepage">
              Taskify
            </Link>
            {isAuthenticated && (
              <div className="hidden md:block">
                <div className="ml-10 flex items-baseline space-x-4" role="menubar">
                  <Link href="/dashboard" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-600" role="menuitem">
                    Dashboard
                  </Link>
                  <Link href="/tasks" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-600" role="menuitem">
                    My Tasks
                  </Link>
                </div>
              </div>
            )}
          </div>

          <div className="flex items-center">
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <span className="text-sm" aria-live="polite">Welcome, {user?.name || user?.email}</span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 text-sm font-medium bg-red-600 hover:bg-red-700 rounded-md transition"
                  aria-label="Log out of your account"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="space-x-4" role="menubar">
                <Link href="/login" className="px-3 py-2 text-sm font-medium hover:bg-indigo-600 rounded-md transition" role="menuitem" aria-label="Sign in to your account">
                  Login
                </Link>
                <Link href="/signup" className="px-3 py-2 text-sm font-medium bg-white text-indigo-700 hover:bg-gray-100 rounded-md transition" role="menuitem" aria-label="Create a new account">
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;