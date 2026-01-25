'use client';

import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';

export default function HomePage() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <header className="flex justify-between items-center mb-12">
          <h1 className="text-3xl font-bold text-indigo-700">Taskify</h1>
          <nav>
            {isAuthenticated ? (
              <Link href="/dashboard" className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition">
                Dashboard
              </Link>
            ) : (
              <div className="space-x-4">
                <Link href="/login" className="px-4 py-2 text-indigo-600 hover:text-indigo-800 font-medium">
                  Log in
                </Link>
                <Link href="/signup" className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition">
                  Sign up
                </Link>
              </div>
            )}
          </nav>
        </header>

        <main className="flex flex-col items-center text-center">
          <h2 className="text-5xl font-bold text-gray-800 mb-6">
            Simplify Your Tasks, Amplify Your Productivity
          </h2>
          <p className="text-xl text-gray-600 mb-10 max-w-2xl">
            Taskify helps you organize your tasks efficiently. Sign up to get started and manage your daily activities with ease.
          </p>

          {!isAuthenticated && (
            <Link
              href="/signup"
              className="px-8 py-4 bg-indigo-600 text-white text-lg font-semibold rounded-lg shadow-lg hover:bg-indigo-700 transition transform hover:scale-105"
            >
              Get Started for Free
            </Link>
          )}

          {isAuthenticated && (
            <Link
              href="/dashboard"
              className="px-8 py-4 bg-green-600 text-white text-lg font-semibold rounded-lg shadow-lg hover:bg-green-700 transition transform hover:scale-105"
            >
              Go to Dashboard
            </Link>
          )}
        </main>
      </div>
    </div>
  );
}