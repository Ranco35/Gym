import { api } from './api';
import { UserRole } from '../types';

interface AuthResponse {
  access: string;
  refresh: string;
  token_type: string;
}

interface UserData {
  email: string;
  username: string;
  role: UserRole;
  full_name?: string;
}

class AuthService {
  private tokenKey = 'auth_token';

  async login(username: string, password: string): Promise<void> {
    try {
      const credentials = {
        username,
        password
      };
      
      const response = await api.post<AuthResponse>('/auth/token', credentials);
      
      if (response.data.access) {
        localStorage.setItem(this.tokenKey, response.data.access);
      } else {
        throw new Error('Token no recibido');
      }
    } catch (error) {
      console.error('Error en login:', error);
      throw new Error('Error al iniciar sesión');
    }
  }

  async register(userData: {
    email: string;
    password: string;
    username: string;
    role?: UserRole;
  }): Promise<void> {
    try {
      const response = await api.post<AuthResponse>('/auth/register', userData);
      
      if (response.data.access) {
        localStorage.setItem(this.tokenKey, response.data.access);
      }
    } catch (error) {
      console.error('Error en registro:', error);
      throw new Error('Error al registrar usuario');
    }
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem(this.tokenKey);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }
}

export const authService = new AuthService();