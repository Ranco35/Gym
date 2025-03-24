import { useState, useCallback } from 'react';
import { authService } from '../services/auth/auth.service';
import { ApiError } from '../utils/errorHandling';
import type { LoginCredentials, RegisterData } from '../services/auth/types';

export function useAuth() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(async (email: string, password: string) => {
    try {
      setIsLoading(true);
      setError(null);
      await authService.login({ username: email, password });
      return true;
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred');
      }
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (email: string, password: string, username: string) => {
    try {
      setIsLoading(true);
      setError(null);
      await authService.register({ email, password, username });
      return true;
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred');
      }
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    login,
    register,
    isLoading,
    error,
    clearError: () => setError(null)
  };
}