import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiResponse, ApiError } from '@/types/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // With httpOnly cookies, authentication headers are handled automatically by the browser
    // The cookies will be sent with each request automatically

    // Add response interceptor to handle errors globally
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        // Handle specific error cases
        if (error.response?.status === 401) {
          // Session might be expired, emit an event for the app to handle
          window.dispatchEvent(new Event('unauthorized'));
        } else if (error.response?.status === 403) {
          // Access denied
          console.error('Access denied:', error);
        } else if (error.response?.status === 404) {
          // Resource not found
          console.error('Resource not found:', error);
        } else if (error.code === 'ECONNABORTED' || error.code === 'ERR_NETWORK') {
          // Network error or timeout
          console.error('Network error:', error);
        }

        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.get<T>(url, config);
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.post<T>(url, data, config);
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.put<T>(url, data, config);
  }

  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.patch<T>(url, data, config);
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.delete<T>(url, config);
  }

  // Specific API methods for tasks
  async getTasks(filters?: any) {
    const queryString = new URLSearchParams(filters).toString();
    const url = `/api/v1/tasks${queryString ? '?' + queryString : ''}`;
    return this.get(url);
  }

  async createTask(data: any) {
    return this.post('/api/v1/tasks', data);
  }

  async updateTask(taskId: string, data: any) {
    return this.put(`/api/v1/tasks/${taskId}`, data);
  }

  async patchTask(taskId: string, data: any) {
    return this.patch(`/api/v1/tasks/${taskId}`, data);
  }

  async deleteTask(taskId: string) {
    return this.delete(`/api/v1/tasks/${taskId}`);
  }

  // Specific API methods for authentication
  async login(credentials: any) {
    return this.post('/api/auth/signin', credentials);
  }

  async register(userData: any) {
    return this.post('/api/auth/signup', userData);
  }

  async logout() {
    return this.post('/api/auth/signout');
  }

  async getCurrentUser() {
    return this.get('/api/auth/me');
  }
}

export const apiClient = new ApiClient();

export default ApiClient;