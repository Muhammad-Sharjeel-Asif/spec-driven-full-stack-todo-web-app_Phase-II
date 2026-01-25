export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: string; // ISO 8601 format
  updatedAt: string; // ISO 8601 format
  emailVerified: boolean;
}

export interface AuthUser {
  user: User;
  token: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials extends LoginCredentials {
  name: string;
}