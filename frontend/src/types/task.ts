export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  dueDate?: string; // ISO 8601 format
  createdAt: string; // ISO 8601 format
  updatedAt: string; // ISO 8601 format
  userId: string;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
  dueDate?: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  completed?: boolean;
  dueDate?: string;
}