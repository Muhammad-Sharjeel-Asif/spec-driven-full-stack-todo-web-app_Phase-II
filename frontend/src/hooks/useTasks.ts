import { useState, useEffect } from 'react';
import { Task, CreateTaskRequest, UpdateTaskRequest } from '@/types/task';
import { apiClient } from '@/lib/api-client';
import { useAuth } from '@/hooks/useAuth';

export const useTasks = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  // Fetch tasks for the authenticated user
  const fetchTasks = async (filters?: any) => {
    if (!user) return;

    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.getTasks(filters);
      setTasks(response.data);
    } catch (err: any) {
      if (err?.response?.status === 401) {
        setError('Session expired. Please log in again.');
      } else if (err?.response?.status === 403) {
        setError('Access denied. You do not have permission to view these tasks.');
      } else if (err?.response?.status === 404) {
        setError('Tasks not found.');
      } else if (err?.code === 'ECONNABORTED' || err?.code === 'ERR_NETWORK') {
        setError('Unable to connect to the server. Please check your internet connection.');
      } else {
        setError(err.message || 'Failed to fetch tasks');
      }
    } finally {
      setLoading(false);
    }
  };

  // Create a new task
  const createTask = async (taskData: CreateTaskRequest) => {
    if (!user) return;

    try {
      setLoading(true);
      const response = await apiClient.createTask(taskData);
      setTasks(prev => [...prev, response.data]);
      return response.data;
    } catch (err: any) {
      if (err?.response?.status === 401) {
        setError('Session expired. Please log in again.');
      } else if (err?.response?.status === 403) {
        setError('Access denied. You do not have permission to create tasks.');
      } else if (err?.response?.status === 400) {
        setError('Invalid task data provided.');
      } else if (err?.code === 'ECONNABORTED' || err?.code === 'ERR_NETWORK') {
        setError('Unable to connect to the server. Please check your internet connection.');
      } else {
        setError(err.message || 'Failed to create task');
      }
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Update an existing task
  const updateTask = async (taskId: string, taskData: UpdateTaskRequest) => {
    if (!user) return;

    try {
      setLoading(true);
      const response = await apiClient.updateTask(taskId, taskData);
      setTasks(prev => prev.map(task => task.id === taskId ? response.data : task));
      return response.data;
    } catch (err: any) {
      if (err?.response?.status === 401) {
        setError('Session expired. Please log in again.');
      } else if (err?.response?.status === 403) {
        setError('Access denied. You do not have permission to update this task.');
      } else if (err?.response?.status === 404) {
        setError('Task not found.');
      } else if (err?.code === 'ECONNABORTED' || err?.code === 'ERR_NETWORK') {
        setError('Unable to connect to the server. Please check your internet connection.');
      } else {
        setError(err.message || 'Failed to update task');
      }
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Toggle task completion status with optimistic update
  const toggleTaskCompletion = async (taskId: string) => {
    if (!user) return;

    try {
      // Optimistic update: immediately update UI
      setTasks(prev => prev.map(task =>
        task.id === taskId ? { ...task, completed: !task.completed } : task
      ));

      const response = await apiClient.patchTask(taskId, {
        completed: !tasks.find(t => t.id === taskId)?.completed
      });

      // Update with server response to ensure consistency
      setTasks(prev => prev.map(task =>
        task.id === taskId ? response.data : task
      ));

      return response.data;
    } catch (err: any) {
      // Revert optimistic update on error
      setTasks(prev => prev.map(task =>
        task.id === taskId ? { ...task, completed: !task.completed } : task
      ));

      if (err?.response?.status === 401) {
        setError('Session expired. Please log in again.');
      } else if (err?.response?.status === 403) {
        setError('Access denied. You do not have permission to update this task.');
      } else if (err?.response?.status === 404) {
        setError('Task not found.');
      } else if (err?.code === 'ECONNABORTED' || err?.code === 'ERR_NETWORK') {
        setError('Unable to connect to the server. Please check your internet connection.');
      } else {
        setError(err.message || 'Failed to update task completion');
      }
      throw err;
    }
  };

  // Delete a task with optimistic update
  const deleteTask = async (taskId: string) => {
    if (!user) return;

    // Optimistic update: immediately remove from UI
    const deletedTask = tasks.find(task => task.id === taskId);
    setTasks(prev => prev.filter(task => task.id !== taskId));

    try {
      await apiClient.deleteTask(taskId);
    } catch (err: any) {
      // Revert optimistic update on error
      if (deletedTask) {
        setTasks(prev => [...prev, deletedTask]);
      }

      if (err?.response?.status === 401) {
        setError('Session expired. Please log in again.');
      } else if (err?.response?.status === 403) {
        setError('Access denied. You do not have permission to delete this task.');
      } else if (err?.response?.status === 404) {
        setError('Task not found.');
      } else if (err?.code === 'ECONNABORTED' || err?.code === 'ERR_NETWORK') {
        setError('Unable to connect to the server. Please check your internet connection.');
      } else {
        setError(err.message || 'Failed to delete task');
      }
      throw err;
    }
  };

  // Filter tasks based on criteria
  const filterTasks = (filterType: 'all' | 'active' | 'completed', dateFilter?: 'today' | 'week' | 'month' | 'overdue') => {
    let filteredTasks = [...tasks];

    // Apply status filter
    switch (filterType) {
      case 'active':
        filteredTasks = filteredTasks.filter(task => !task.completed);
        break;
      case 'completed':
        filteredTasks = filteredTasks.filter(task => task.completed);
        break;
      default:
        // No filter applied
        break;
    }

    // Apply date filter if specified
    if (dateFilter) {
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

      filteredTasks = filteredTasks.filter(task => {
        if (!task.dueDate) return true; // Tasks without due dates pass all date filters

        const dueDate = new Date(task.dueDate);

        switch (dateFilter) {
          case 'today':
            const taskDueDate = new Date(dueDate.getFullYear(), dueDate.getMonth(), dueDate.getDate());
            return taskDueDate.getTime() === today.getTime();
          case 'week':
            const weekFromNow = new Date(today);
            weekFromNow.setDate(today.getDate() + 7);
            return dueDate >= today && dueDate <= weekFromNow;
          case 'month':
            const monthFromNow = new Date(today);
            monthFromNow.setMonth(today.getMonth() + 1);
            return dueDate >= today && dueDate <= monthFromNow;
          case 'overdue':
            return dueDate < today && !task.completed;
          default:
            return true;
        }
      });
    }

    return filteredTasks;
  };

  // Load tasks when user is available
  useEffect(() => {
    if (user) {
      fetchTasks();
    }
  }, [user?.id]);

  return {
    tasks,
    loading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    toggleTaskCompletion,
    deleteTask,
    filterTasks,
  };
};