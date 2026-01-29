import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { tasksApi } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const TaskDetail = ({ taskId, userId }) => {
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const { user } = useAuth();
  const params = useParams(); // For route-based task ID

  // Use either the passed taskId, the route param, or the current user's ID
  const taskIdToUse = taskId || params?.taskId;
  const userIdToUse = userId || user?.id;

  useEffect(() => {
    if (taskIdToUse && userIdToUse) {
      fetchTaskDetail();
    }
  }, [taskIdToUse, userIdToUse]);

  const fetchTaskDetail = async () => {
    try {
      setLoading(true);
      setError('');

      if (!userIdToUse) {
        throw new Error('No user ID available');
      }

      if (!taskIdToUse) {
        throw new Error('No task ID available');
      }

      const taskData = await tasksApi.getUserTask(userIdToUse, taskIdToUse);
      setTask(taskData);
    } catch (err) {
      setError(err.message || 'Failed to fetch task details');
      console.error('Error fetching task details:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleCompletion = async () => {
    try {
      setLoading(true);
      await tasksApi.toggleTaskCompletion(userIdToUse, taskIdToUse);
      // Refresh task details after toggling completion
      fetchTaskDetail();
      // Show success feedback
      alert(`Task marked as ${task.is_completed ? 'incomplete' : 'complete'}!`);
    } catch (err) {
      setError(err.message || 'Failed to update task completion');
      console.error('Error updating task completion:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTask = async () => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return; // User cancelled the deletion
    }

    try {
      setLoading(true);
      await tasksApi.deleteUserTask(userIdToUse, taskIdToUse);
      // Show success feedback
      alert('Task deleted successfully!');
      // Optionally redirect or notify parent component
      if (typeof onDelete === 'function') {
        onDelete(taskIdToUse);
      }
    } catch (err) {
      setError(err.message || 'Failed to delete task');
      console.error('Error deleting task:', err);
    } finally {
      setLoading(false);
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

  if (!task) {
    return (
      <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded relative" role="alert">
        <span className="block sm:inline">Task not found</span>
      </div>
    );
  }

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
      <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className={`text-lg leading-6 font-medium ${
            task.is_completed ? 'line-through text-gray-400' : 'text-gray-900'
          }`}>
            {task.title}
          </h3>
          <div className="flex items-center space-x-3">
            <button
              onClick={handleToggleCompletion}
              className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                task.is_completed
                  ? 'bg-green-100 text-green-800 hover:bg-green-200'
                  : 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
              } transition-colors`}
            >
              {task.is_completed ? 'Completed' : 'Mark Complete'}
            </button>
            <button
              onClick={handleDeleteTask}
              className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800 hover:bg-red-200 transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
      <div className="px-4 py-5 sm:p-6">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div>
            <h4 className="text-sm font-medium text-gray-500">Description</h4>
            <div className="mt-1 text-sm text-gray-900">
              {task.description || <span className="text-gray-400 italic">No description provided</span>}
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-medium text-gray-500">Priority</h4>
              <div className="mt-1">
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  task.priority === 3 ? 'bg-red-100 text-red-800' :
                  task.priority === 2 ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {task.priority === 3 ? 'High' : task.priority === 2 ? 'Medium' : 'Low'} Priority
                </span>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-500">Status</h4>
              <div className="mt-1">
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  task.is_completed ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {task.is_completed ? 'Completed' : 'Pending'}
                </span>
              </div>
            </div>

            {task.due_date && (
              <div>
                <h4 className="text-sm font-medium text-gray-500">Due Date</h4>
                <div className="mt-1 text-sm text-gray-900">
                  {new Date(task.due_date).toLocaleDateString()}
                  {' '}
                  {new Date(task.due_date) < new Date() && !task.is_completed && (
                    <span className="inline-block ml-2 px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">
                      Overdue
                    </span>
                  )}
                </div>
              </div>
            )}

            <div>
              <h4 className="text-sm font-medium text-gray-500">Created</h4>
              <div className="mt-1 text-sm text-gray-900">
                {new Date(task.created_at).toLocaleString()}
              </div>
            </div>

            {task.updated_at && (
              <div>
                <h4 className="text-sm font-medium text-gray-500">Last Updated</h4>
                <div className="mt-1 text-sm text-gray-900">
                  {new Date(task.updated_at).toLocaleString()}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaskDetail;