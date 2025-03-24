export interface AuthResponse {
  access: string;
  refresh: string;
  token_type: string;
  username?: string;
  email?: string;
  role?: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  username: string;
  password2?: string;
  role?: string;
}