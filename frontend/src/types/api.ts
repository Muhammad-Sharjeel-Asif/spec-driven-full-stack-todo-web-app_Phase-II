export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
}

export interface ApiError {
  code: string;
  message: string;
  details?: FieldError[];
}

export interface FieldError {
  field: string;
  message: string;
}

export interface PaginationParams {
  page?: number;
  limit?: number;
}

export interface TaskFilterParams {
  filter?: 'all' | 'active' | 'completed';
  sortBy?: 'dueDate' | 'createdAt' | 'updatedAt';
  sortOrder?: 'asc' | 'desc';
}