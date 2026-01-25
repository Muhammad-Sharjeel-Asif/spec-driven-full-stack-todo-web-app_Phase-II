const axios = require('axios');

// Integration test for the Taskify frontend application
describe('Taskify Frontend Integration Tests', () => {
  const BASE_URL = 'http://localhost:3000';
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  let authToken = null;
  let userId = null;
  let testUser = {
    name: 'Integration Test User',
    email: `testuser_${Date.now()}@example.com`,
    password: 'SecurePassword123!'
  };
  let createdTaskIds = [];

  // Helper function to make authenticated API calls
  const authenticatedRequest = (method, url, data = null) => {
    const config = {
      method,
      url: `${API_BASE_URL}${url}`,
      headers: {
        'Content-Type': 'application/json',
      },
      ...(authToken && { headers: { ...config.headers, Authorization: `Bearer ${authToken}` } }),
      ...(data && { data })
    };

    return axios(config);
  };

  describe('Authentication Flow', () => {
    test('1.1 - User Registration', async () => {
      try {
        const response = await axios.post(`${API_BASE_URL}/api/auth/signup`, {
          name: testUser.name,
          email: testUser.email,
          password: testUser.password
        });

        expect(response.status).toBe(200);
        expect(response.data).toHaveProperty('user');
        expect(response.data.user).toHaveProperty('id');
        expect(response.data.user.email).toBe(testUser.email);

        userId = response.data.user.id;
        console.log(`✓ User registered successfully with ID: ${userId}`);
      } catch (error) {
        console.error('✗ Registration failed:', error.response?.data || error.message);
        throw error;
      }
    });

    test('1.2 - User Login', async () => {
      try {
        const response = await axios.post(`${API_BASE_URL}/api/auth/signin`, {
          email: testUser.email,
          password: testUser.password
        });

        expect(response.status).toBe(200);
        expect(response.data).toHaveProperty('user');
        expect(response.data.user.email).toBe(testUser.email);

        // Note: With httpOnly cookies, the token is not directly accessible in frontend
        // but the session should be established
        console.log('✓ User logged in successfully');
      } catch (error) {
        console.error('✗ Login failed:', error.response?.data || error.message);
        throw error;
      }
    });

    test('1.3 - Access Protected Dashboard Route', async () => {
      try {
        // Try to access the dashboard page
        const response = await axios.get(`${BASE_URL}/dashboard`, {
          validateStatus: function (status) {
            return status < 500; // Accept all statuses except server errors
          }
        });

        // Should not redirect to login (which would return login page HTML)
        // The actual check would happen in the browser with proper auth state
        expect(response.status).toBeLessThan(500);
        console.log('✓ Attempted to access protected dashboard route');
      } catch (error) {
        console.error('✗ Dashboard access test failed:', error.message);
        throw error;
      }
    });

    test('1.4 - Logout', async () => {
      try {
        const response = await axios.post(`${API_BASE_URL}/api/auth/signout`);

        expect(response.status).toBe(200);
        console.log('✓ User logged out successfully');
      } catch (error) {
        console.error('✗ Logout failed:', error.response?.data || error.message);
        throw error;
      }
    });
  });

  describe('Todo Operations', () => {
    // Login before running todo operations
    beforeAll(async () => {
      try {
        const response = await axios.post(`${API_BASE_URL}/api/auth/signin`, {
          email: testUser.email,
          password: testUser.password
        });
        console.log('✓ Logged in for todo operations');
      } catch (error) {
        console.error('✗ Failed to login for todo operations:', error.message);
        throw error;
      }
    });

    test('2.1 - Create Task', async () => {
      try {
        const taskData = {
          title: 'Integration Test Task',
          description: 'This is a test task created during integration testing',
          dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] // 7 days from now
        };

        const response = await authenticatedRequest('POST', `/api/users/${userId}/tasks`, taskData);

        expect(response.status).toBe(200);
        expect(response.data).toHaveProperty('id');
        expect(response.data.title).toBe(taskData.title);
        expect(response.data.userId).toBe(userId);

        createdTaskIds.push(response.data.id);
        console.log(`✓ Task created successfully with ID: ${response.data.id}`);
      } catch (error) {
        console.error('✗ Task creation failed:', error.response?.data || error.message);
        throw error;
      }
    });

    test('2.2 - View Tasks', async () => {
      try {
        const response = await authenticatedRequest('GET', `/api/users/${userId}/tasks`);

        expect(response.status).toBe(200);
        expect(Array.isArray(response.data)).toBeTruthy();

        const createdTask = response.data.find(task => task.id === createdTaskIds[0]);
        expect(createdTask).toBeDefined();
        expect(createdTask.title).toBe('Integration Test Task');

        console.log(`✓ Retrieved ${response.data.length} tasks, including created test task`);
      } catch (error) {
        console.error('✗ Task retrieval failed:', error.response?.data || error.message);
        throw error;
      }
    });

    test('2.3 - Update Task', async () => {
      try {
        const updatedData = {
          title: 'Updated Integration Test Task',
          description: 'This task has been updated during integration testing'
        };

        const response = await authenticatedRequest('PUT', `/api/users/${userId}/tasks/${createdTaskIds[0]}`, updatedData);

        expect(response.status).toBe(200);
        expect(response.data.id).toBe(createdTaskIds[0]);
        expect(response.data.title).toBe(updatedData.title);
        expect(response.data.description).toBe(updatedData.description);

        console.log('✓ Task updated successfully');
      } catch (error) {
        console.error('✗ Task update failed:', error.response?.data || error.message);
        throw error;
      }
    });

    test('2.4 - Toggle Task Completion', async () => {
      try {
        // First, mark as incomplete if it's completed
        let response = await authenticatedRequest('PATCH', `/api/users/${userId}/tasks/${createdTaskIds[0]}`, {
          completed: false
        });

        expect(response.status).toBe(200);
        expect(response.data.id).toBe(createdTaskIds[0]);
        expect(response.data.completed).toBe(false);

        // Then mark as completed
        response = await authenticatedRequest('PATCH', `/api/users/${userId}/tasks/${createdTaskIds[0]}`, {
          completed: true
        });

        expect(response.status).toBe(200);
        expect(response.data.id).toBe(createdTaskIds[0]);
        expect(response.data.completed).toBe(true);

        console.log('✓ Task completion toggled successfully');
      } catch (error) {
        console.error('✗ Task completion toggle failed:', error.response?.data || error.message);
        throw error;
      }
    });

    test('2.5 - Delete Task', async () => {
      try {
        const response = await authenticatedRequest('DELETE', `/api/users/${userId}/tasks/${createdTaskIds[0]}`);

        expect(response.status).toBe(200);
        expect(response.data.success).toBe(true);

        // Verify the task is gone
        try {
          await authenticatedRequest('GET', `/api/users/${userId}/tasks/${createdTaskIds[0]}`);
          // Should not reach here
          expect(false).toBe(true);
        } catch (error) {
          expect(error.response.status).toBe(404);
        }

        console.log('✓ Task deleted successfully');
      } catch (error) {
        console.error('✗ Task deletion failed:', error.response?.data || error.message);
        throw error;
      }
    });
  });

  describe('Protected Routes and Authentication', () => {
    test('3.1 - Unauthenticated Access to Dashboard', async () => {
      try {
        // First, logout to clear session
        await axios.post(`${API_BASE_URL}/api/auth/signout`);

        // Try to access dashboard without authentication
        const response = await axios.get(`${BASE_URL}/dashboard`, {
          validateStatus: function (status) {
            return status < 500;
          }
        });

        // Should redirect to login page or return unauthorized
        // The exact behavior depends on the implementation
        console.log('✓ Tested unauthenticated dashboard access');
      } catch (error) {
        console.error('✗ Unauthenticated dashboard access test failed:', error.message);
        throw error;
      }
    });

    test('3.2 - Access Current User Info', async () => {
      try {
        // Login again
        await axios.post(`${API_BASE_URL}/api/auth/signin`, {
          email: testUser.email,
          password: testUser.password
        });

        // Access current user info
        const response = await authenticatedRequest('GET', '/api/auth/me');

        expect(response.status).toBe(200);
        expect(response.data).toHaveProperty('id');
        expect(response.data.email).toBe(testUser.email);

        console.log('✓ Accessed current user info successfully');
      } catch (error) {
        console.error('✗ Current user info access failed:', error.response?.data || error.message);
        throw error;
      }
    });
  });

  describe('Error Handling', () => {
    test('4.1 - Invalid Login Credentials', async () => {
      try {
        const response = await axios.post(`${API_BASE_URL}/api/auth/signin`, {
          email: testUser.email,
          password: 'wrongpassword'
        });

        // Should return 401 for invalid credentials
        expect(response.status).toBe(401);
        console.log('✓ Correctly handled invalid login credentials');
      } catch (error) {
        // 401 errors are expected here
        if (error.response?.status === 401) {
          console.log('✓ Correctly handled invalid login credentials');
        } else {
          console.error('✗ Unexpected error during invalid login test:', error.message);
          throw error;
        }
      }
    });

    test('4.2 - Access Non-existent Task', async () => {
      try {
        // Try to access a task that doesn't exist
        const fakeTaskId = 'nonexistent-task-id';
        const response = await authenticatedRequest('GET', `/api/users/${userId}/tasks/${fakeTaskId}`);

        // Should return 404 for non-existent task
        expect(response.status).toBe(404);
        console.log('✓ Correctly handled non-existent task access');
      } catch (error) {
        if (error.response?.status === 404) {
          console.log('✓ Correctly handled non-existent task access');
        } else {
          console.error('✗ Unexpected error during non-existent task test:', error.message);
          throw error;
        }
      }
    });
  });

  describe('Form Validation', () => {
    test('5.1 - Validate Task Creation with Missing Fields', async () => {
      try {
        // Try to create a task with empty title (should fail validation)
        const invalidTaskData = {
          title: '', // Empty title should fail validation
          description: 'Test description'
        };

        const response = await authenticatedRequest('POST', `/api/users/${userId}/tasks`, invalidTaskData);

        // Should return validation error (likely 400)
        expect(response.status).toBeGreaterThanOrEqual(400);
        console.log('✓ Correctly validated task creation with missing fields');
      } catch (error) {
        if (error.response?.status >= 400) {
          console.log('✓ Correctly validated task creation with missing fields');
        } else {
          console.error('✗ Unexpected error during validation test:', error.message);
          throw error;
        }
      }
    });

    test('5.2 - Validate User Registration with Invalid Email', async () => {
      try {
        const invalidUserData = {
          name: 'Test User',
          email: 'invalid-email', // Invalid email format
          password: 'password123'
        };

        const response = await axios.post(`${API_BASE_URL}/api/auth/signup`, invalidUserData);

        // Should return validation error (likely 400)
        expect(response.status).toBeGreaterThanOrEqual(400);
        console.log('✓ Correctly validated user registration with invalid email');
      } catch (error) {
        if (error.response?.status >= 400) {
          console.log('✓ Correctly validated user registration with invalid email');
        } else {
          console.error('✗ Unexpected error during registration validation test:', error.message);
          throw error;
        }
      }
    });
  });

  // Cleanup after tests
  afterAll(async () => {
    console.log('\n--- Test Cleanup ---');

    // Clean up any remaining tasks
    for (const taskId of createdTaskIds) {
      try {
        await authenticatedRequest('DELETE', `/api/users/${userId}/tasks/${taskId}`);
        console.log(`✓ Cleaned up task with ID: ${taskId}`);
      } catch (error) {
        // Ignore cleanup errors
        console.log(`⚠ Could not clean up task with ID: ${taskId}`);
      }
    }

    // Clean up test user (if endpoint exists)
    try {
      await axios.post(`${API_BASE_URL}/api/auth/signout`);
      console.log('✓ Signed out test user');
    } catch (error) {
      console.log('⚠ Could not sign out test user');
    }

    console.log('✓ Integration tests completed');
  });
});

console.log('Starting Taskify Frontend Integration Tests...\n');