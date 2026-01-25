import { renderHook, act } from '@testing-library/react';
import { useTasks } from '@/hooks/useTasks';
import { apiClient } from '@/lib/api-client';
import { useAuth } from '@/hooks/useAuth';

// Mock the apiClient and useAuth
jest.mock('@/lib/api-client', () => ({
  apiClient: {
    getTasks: jest.fn(),
    createTask: jest.fn(),
    updateTask: jest.fn(),
    patchTask: jest.fn(),
    deleteTask: jest.fn(),
    getCurrentUser: jest.fn(),
    login: jest.fn(),
    register: jest.fn(),
    logout: jest.fn(),
  }
}));

jest.mock('@/hooks/useAuth', () => ({
  useAuth: jest.fn(() => ({ user: { id: 'test-user-id' }, isAuthenticated: true, isLoading: false }))
}));

describe('useTasks', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('initializes with empty tasks and loading state', () => {
    const { result } = renderHook(() => useTasks());

    expect(result.current.tasks).toEqual([]);
    expect(result.current.loading).toBe(true);
  });

  test('fetches tasks successfully', async () => {
    const mockTasks = [
      { id: '1', title: 'Task 1', completed: false, userId: 'test-user-id' },
      { id: '2', title: 'Task 2', completed: true, userId: 'test-user-id' }
    ];

    // Mock the api call
    const { apiClient } = require('../lib/api-client');
    apiClient.getTasks.mockResolvedValue({ data: mockTasks });

    const { result } = renderHook(() => useTasks());

    // Wait for the effect to complete
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(apiClient.getTasks).toHaveBeenCalledWith('test-user-id', undefined);
    expect(result.current.tasks).toEqual(mockTasks);
    expect(result.current.loading).toBe(false);
  });

  test('creates a new task', async () => {
    const newTask = { id: '3', title: 'New Task', completed: false, userId: 'test-user-id' };
    const taskData = { title: 'New Task', description: 'Description' };

    const { apiClient } = require('../lib/api-client');
    apiClient.createTask.mockResolvedValue({ data: newTask });

    const { result } = renderHook(() => useTasks());

    await act(async () => {
      await result.current.createTask(taskData);
    });

    expect(apiClient.createTask).toHaveBeenCalledWith('test-user-id', taskData);
    expect(result.current.tasks).toContainEqual(newTask);
  });

  test('toggles task completion', async () => {
    const initialTasks = [
      { id: '1', title: 'Task 1', completed: false, userId: 'test-user-id' }
    ];

    const updatedTask = { ...initialTasks[0], completed: true };

    const { apiClient } = require('../lib/api-client');
    apiClient.getTasks.mockResolvedValue({ data: initialTasks });
    apiClient.patchTask.mockResolvedValue({ data: updatedTask });

    const { result } = renderHook(() => useTasks());

    // Wait for initial fetch
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    // Toggle completion
    await act(async () => {
      await result.current.toggleTaskCompletion('1');
    });

    expect(apiClient.patchTask).toHaveBeenCalledWith('test-user-id', '1', { completed: true });
    expect(result.current.tasks[0].completed).toBe(true);
  });

  test('deletes a task', async () => {
    const initialTasks = [
      { id: '1', title: 'Task 1', completed: false, userId: 'test-user-id' },
      { id: '2', title: 'Task 2', completed: true, userId: 'test-user-id' }
    ];

    const { apiClient } = require('../lib/api-client');
    apiClient.getTasks.mockResolvedValue({ data: initialTasks });
    apiClient.deleteTask.mockResolvedValue({});

    const { result } = renderHook(() => useTasks());

    // Wait for initial fetch
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    const initialLength = result.current.tasks.length;

    // Delete task
    await act(async () => {
      await result.current.deleteTask('1');
    });

    expect(apiClient.deleteTask).toHaveBeenCalledWith('test-user-id', '1');
    expect(result.current.tasks).toHaveLength(initialLength - 1);
    expect(result.current.tasks.find(task => task.id === '1')).toBeUndefined();
  });
});