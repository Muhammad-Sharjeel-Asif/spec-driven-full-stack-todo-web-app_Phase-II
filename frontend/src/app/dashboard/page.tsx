'use client';

import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import ProtectedRoute from '@/components/Layout/ProtectedRoute';
import { useTasks } from '@/hooks/useTasks';

// Lazy load heavy components for performance
const TaskList = React.lazy(() => import('@/components/TaskList/TaskList'));
const TaskForm = React.lazy(() => import('@/components/TaskForm/TaskForm'));

// Need to import React for lazy loading
import React from 'react';

export default function DashboardPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const { createTask } = useTasks();
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');
  const [dateFilter, setDateFilter] = useState<'today' | 'week' | 'month' | 'overdue' | null>(null);
  const [showForm, setShowForm] = useState(false);

  if (isLoading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  const handleCreateTask = async (formData: any) => {
    try {
      await createTask(formData);
      setShowForm(false);
    } catch (error) {
      console.error('Failed to create task:', error);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
            <h1 className="text-2xl font-bold text-gray-900">Task Dashboard</h1>
          </div>
        </header>

        <main>
          <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">
              <div className="bg-white shadow overflow-hidden sm:rounded-lg p-6">
                <div className="mb-6">
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-semibold text-gray-800">Add New Task</h2>
                    <button
                      onClick={() => setShowForm(!showForm)}
                      className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                    >
                      {showForm ? 'Cancel' : 'Add Task'}
                    </button>
                  </div>

                  {showForm && (
                    <div className="bg-gray-50 p-4 rounded-md">
                      <TaskForm onSubmit={handleCreateTask} submitButtonText="Create Task" />
                    </div>
                  )}
                </div>

                <div>
                  <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4 gap-4">
                    <h2 className="text-xl font-semibold text-gray-800">Your Tasks</h2>
                    <div className="flex flex-wrap gap-2">
                      <div className="flex space-x-1">
                        <button
                          onClick={() => setFilter('all')}
                          className={`px-3 py-1 text-sm rounded-md ${
                            filter === 'all'
                              ? 'bg-indigo-600 text-white'
                              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                          }`}
                        >
                          All
                        </button>
                        <button
                          onClick={() => setFilter('active')}
                          className={`px-3 py-1 text-sm rounded-md ${
                            filter === 'active'
                              ? 'bg-indigo-600 text-white'
                              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                          }`}
                        >
                          Active
                        </button>
                        <button
                          onClick={() => setFilter('completed')}
                          className={`px-3 py-1 text-sm rounded-md ${
                            filter === 'completed'
                              ? 'bg-indigo-600 text-white'
                              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                          }`}
                        >
                          Completed
                        </button>
                      </div>
                      <div className="flex space-x-1">
                        <button
                          onClick={() => setDateFilter(dateFilter === 'today' ? null : 'today')}
                          className={`px-3 py-1 text-sm rounded-md ${
                            dateFilter === 'today'
                              ? 'bg-green-600 text-white'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          Today
                        </button>
                        <button
                          onClick={() => setDateFilter(dateFilter === 'week' ? null : 'week')}
                          className={`px-3 py-1 text-sm rounded-md ${
                            dateFilter === 'week'
                              ? 'bg-green-600 text-white'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          This Week
                        </button>
                        <button
                          onClick={() => setDateFilter(dateFilter === 'month' ? null : 'month')}
                          className={`px-3 py-1 text-sm rounded-md ${
                            dateFilter === 'month'
                              ? 'bg-green-600 text-white'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          This Month
                        </button>
                        <button
                          onClick={() => setDateFilter(dateFilter === 'overdue' ? null : 'overdue')}
                          className={`px-3 py-1 text-sm rounded-md ${
                            dateFilter === 'overdue'
                              ? 'bg-red-600 text-white'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          Overdue
                        </button>
                      </div>
                    </div>
                  </div>

                  <div>
                    <TaskList filter={filter} dateFilter={dateFilter} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}