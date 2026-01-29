// Frontend API client with JWT headers and {user_id} path support
import axios from 'axios';

class ApiClient {
  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
      timeout: 10000, // 10 seconds timeout
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add JWT token to requests
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('jwt_token'); // Or however you store the JWT
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Handle responses and errors
    this.client.interceptors.response.use(
      (response) => {
        return response;
      },
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access - maybe redirect to login
          localStorage.removeItem('jwt_token');
          // Trigger a custom event for other parts of the app to handle
          window.dispatchEvent(new Event('unauthorized'));
          window.location.href = '/login';
        } else if (error.response?.status === 403) {
          // Handle forbidden access
          console.error('Forbidden access:', error.response.data);
          // Could show a specific forbidden error page or message
          window.dispatchEvent(new Event('forbidden'));
        } else if (error.response?.status === 404) {
          // Handle not found errors
          console.error('Resource not found:', error.response.data);
        } else if (error.response?.status >= 500) {
          // Handle server errors
          console.error('Server error:', error.response.data);
        }

        return Promise.reject(error);
      }
    );
  }

  // AUTHENTICATION ENDPOINTS
  async register(userData) {
    try {
      const response = await this.client.post('/api/auth/register', userData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async login(credentials) {
    try {
      const response = await this.client.post('/api/auth/login', credentials);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async logout() {
    try {
      const response = await this.client.post('/api/auth/logout');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getCurrentUser() {
    try {
      const response = await this.client.get('/api/auth/me');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // USER-SCOPED TASK ENDPOINTS
  async getUserTasks(userId, filters = {}) {
    try {
      const params = new URLSearchParams();

      // Add filters to query parameters
      Object.keys(filters).forEach(key => {
        if (filters[key] !== undefined && filters[key] !== null) {
          params.append(key, filters[key]);
        }
      });

      const queryString = params.toString();
      const url = `/api/${userId}/tasks${queryString ? '?' + queryString : ''}`;

      const response = await this.client.get(url);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async createUserTask(userId, taskData) {
    try {
      const response = await this.client.post(`/api/${userId}/tasks`, taskData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getUserTask(userId, taskId) {
    try {
      const response = await this.client.get(`/api/${userId}/tasks/${taskId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateUserTask(userId, taskId, taskData) {
    try {
      const response = await this.client.put(`/api/${userId}/tasks/${taskId}`, taskData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async deleteUserTask(userId, taskId) {
    try {
      const response = await this.client.delete(`/api/${userId}/tasks/${taskId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async toggleTaskCompletion(userId, taskId) {
    try {
      const response = await this.client.patch(`/api/${userId}/tasks/${taskId}/complete`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getUserTaskStats(userId) {
    try {
      const response = await this.client.get(`/api/${userId}/tasks/stats`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // HELPER METHODS
  handleError(error) {
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      return {
        status,
        message: data.detail || data.message || 'An error occurred',
        data: data
      };
    } else if (error.request) {
      // Request was made but no response received
      return {
        status: 0,
        message: 'Network error - no response received',
        data: null
      };
    } else {
      // Something else happened
      return {
        status: 0,
        message: error.message || 'An unexpected error occurred',
        data: null
      };
    }
  }

  // SET AUTH TOKEN (if needed externally)
  setAuthToken(token) {
    if (token) {
      this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete this.client.defaults.headers.common['Authorization'];
    }
  }

  // CLEAR AUTH TOKEN
  clearAuthToken() {
    delete this.client.defaults.headers.common['Authorization'];
  }
}

// Export a singleton instance
const apiClient = new ApiClient();
export default apiClient;

// Export individual functions for convenience
export const authApi = {
  register: (userData) => apiClient.register(userData),
  login: (credentials) => apiClient.login(credentials),
  logout: () => apiClient.logout(),
  getCurrentUser: () => apiClient.getCurrentUser(),
};

export const tasksApi = {
  getUserTasks: (userId, filters) => apiClient.getUserTasks(userId, filters),
  createUserTask: (userId, taskData) => apiClient.createUserTask(userId, taskData),
  getUserTask: (userId, taskId) => apiClient.getUserTask(userId, taskId),
  updateUserTask: (userId, taskId, taskData) => apiClient.updateUserTask(userId, taskId, taskData),
  deleteUserTask: (userId, taskId) => apiClient.deleteUserTask(userId, taskId),
  toggleTaskCompletion: (userId, taskId) => apiClient.toggleTaskCompletion(userId, taskId),
  getUserTaskStats: (userId) => apiClient.getUserTaskStats(userId),
};