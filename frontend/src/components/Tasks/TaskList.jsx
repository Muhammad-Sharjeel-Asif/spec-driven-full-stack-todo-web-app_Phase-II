import React, { useState, useEffect } from 'react';
import { tasksApi } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const TaskList = ({ userId }) => {
  const [tasks, setTasks] = useState([]);
  const [filteredTasks, setFilteredTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Filtering states
  const [statusFilter, setStatusFilter] = useState('all'); // 'all', 'completed', 'pending'
  const [priorityFilter, setPriorityFilter] = useState('all'); // 'all', 'high', 'medium', 'low'
  const [searchQuery, setSearchQuery] = useState('');

  const { user } = useAuth();

  useEffect(() => {
    if (userId) {
      fetchTasks();
    }
  }, [userId]);

  useEffect(() => {
    // Apply filtering when tasks or filters change
    applyFilters();
  }, [tasks, statusFilter, priorityFilter, searchQuery]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError('');

      // Use the current user's ID if userId is not provided
      const targetUserId = userId || user?.id;

      if (!targetUserId) {
        throw new Error('No user ID available');
      }

      const taskData = await tasksApi.getUserTasks(targetUserId);
      setTasks(taskData);
    } catch (err) {
      setError(err.message || 'Failed to fetch tasks');
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let result = [...tasks];

    // Apply status filter
    if (statusFilter !== 'all') {
      if (statusFilter === 'completed') {
        result = result.filter(task => task.is_completed);
      } else if (statusFilter === 'pending') {
        result = result.filter(task => !task.is_completed);
      }
    }

    // Apply priority filter
    if (priorityFilter !== 'all') {
      if (priorityFilter === 'high') {
        result = result.filter(task => task.priority === 3);
      } else if (priorityFilter === 'medium') {
        result = result.filter(task => task.priority === 2);
      } else if (priorityFilter === 'low') {
        result = result.filter(task => task.priority === 1);
      }
    }

    // Apply search query filter (search in title and description)
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(task =>
        task.title.toLowerCase().includes(query) ||
        (task.description && task.description.toLowerCase().includes(query))
      );
    }

    setFilteredTasks(result);
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return; // User cancelled the deletion
    }

    try {
      setLoading(true);
      await tasksApi.deleteUserTask(userId, taskId);
      // Refresh the task list after deletion
      fetchTasks();
      // Show success feedback
      alert('Task deleted successfully!');
    } catch (err) {
      setError(err.message || 'Failed to delete task');
      console.error('Error deleting task:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleCompletion = async (updatedTask) => {
    try {
      await tasksApi.toggleTaskCompletion(userId, updatedTask.id);
      // Refresh the task list after toggling completion
      fetchTasks();
    } catch (err) {
      setError(err.message || 'Failed to update task completion');
      console.error('Error updating task completion:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <span className="block sm:inline">{error}</span>
      </div>
    );
  }

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md">
      {/* Filtering Controls */}
      <div className="p-4 bg-gray-50 border-b border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search Input */}
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
              Search
            </label>
            <input
              type="text"
              id="search"
              placeholder="Search tasks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>

          {/* Status Filter */}
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              id="status"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
              <option value="all">All</option>
              <option value="pending">Pending</option>
              <option value="completed">Completed</option>
            </select>
          </div>

          {/* Priority Filter */}
          <div>
            <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
              Priority
            </label>
            <select
              id="priority"
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
              <option value="all">All Priorities</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          {/* Results Count */}
          <div className="flex items-end">
            <p className="text-sm text-gray-500">
              Showing {filteredTasks.length} of {tasks.length} tasks
            </p>
          </div>
        </div>
      </div>

      {/* Task List */}
      <ul className="divide-y divide-gray-200">
        {filteredTasks.length === 0 ? (
          <li className="px-4 py-4 sm:px-6">
            <p className="text-gray-500">No tasks found. {tasks.length > 0 ? 'Try changing your filters.' : 'Create your first task!'}</p>
          </li>
        ) : (
          filteredTasks.map((task) => (
            <li key={task.id} className="px-4 py-4 sm:px-6 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <TaskToggle
                    task={{
                      ...task,
                      completed: task.is_completed
                    }}
                    onUpdate={handleToggleCompletion}
                    externalLoading={loading}
                  />
                  <div>
                    <h3 className={`text-sm font-medium ${task.is_completed ? 'line-through text-gray-400' : 'text-gray-900'}`}>
                      {task.title}
                    </h3>
                    <p className="text-sm text-gray-500 truncate max-w-xs">{task.description || 'No description'}</p>

                    {/* Task metadata */}
                    <div className="mt-1 flex flex-wrap gap-2">
                      {task.priority && (
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          task.priority === 3 ? 'bg-red-100 text-red-800' :
                          task.priority === 2 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {task.priority === 3 ? 'High' : task.priority === 2 ? 'Medium' : 'Low'} Priority
                        </span>
                      )}

                      {task.due_date && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          Due: {new Date(task.due_date).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleDeleteTask(task.id)}
                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 hover:bg-red-200 transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </li>
          ))
        )}
      </ul>
    </div>
  );
};

export default TaskList;