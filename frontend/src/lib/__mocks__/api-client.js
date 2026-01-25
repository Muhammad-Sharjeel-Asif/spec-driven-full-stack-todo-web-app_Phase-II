// Mock for the API client to prevent network requests during tests
export const apiClient = {
  get: jest.fn(() => Promise.resolve({ data: {}, status: 200 })),
  post: jest.fn(() => Promise.resolve({ data: {}, status: 200 })),
  put: jest.fn(() => Promise.resolve({ data: {}, status: 200 })),
  patch: jest.fn(() => Promise.resolve({ data: {}, status: 200 })),
  delete: jest.fn(() => Promise.resolve({ data: {}, status: 200 })),
  getTasks: jest.fn(() => Promise.resolve({ data: [] })),
  createTask: jest.fn(() => Promise.resolve({ data: {} })),
  updateTask: jest.fn(() => Promise.resolve({ data: {} })),
  patchTask: jest.fn(() => Promise.resolve({ data: {} })),
  deleteTask: jest.fn(() => Promise.resolve({})),
  login: jest.fn(() => Promise.resolve({ data: { user: { id: 'test-user', name: 'Test User', email: 'test@example.com' } } })),
  register: jest.fn(() => Promise.resolve({ data: { user: { id: 'test-user', name: 'Test User', email: 'test@example.com' } } })),
  logout: jest.fn(() => Promise.resolve({})),
  getCurrentUser: jest.fn(() => Promise.resolve({ data: { id: 'test-user', name: 'Test User', email: 'test@example.com' } })),
};

export default apiClient;