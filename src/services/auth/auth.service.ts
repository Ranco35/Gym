import { api } from '../api';
import { AuthResponse, LoginCredentials, RegisterData } from './types';
import { ApiError } from '../../utils/errorHandling';

class AuthService {
  private tokenKey = 'auth_token';

  async login({ username, password }: LoginCredentials): Promise<void> {
    try {
      const { data } = await api.post<AuthResponse>('/auth/token', {
        username,
        password
      });
      
      if (!data.access) {
        throw new ApiError('Invalid response from server');
      }

      localStorage.setItem(this.tokenKey, data.access);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError('Failed to authenticate');
    }
  }

  async register(userData: RegisterData): Promise<void> {
    try {
      const { data } = await api.post<AuthResponse>('/auth/register', userData);
      
      if (!data.access) {
        throw new ApiError('Invalid response from server');
      }

      localStorage.setItem(this.tokenKey, data.access);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError('Failed to register user');
    }
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }
}

export const authService = new AuthService();