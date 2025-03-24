import React, { useState, useCallback } from 'react';
import { LoginForm } from './LoginForm';
import { RegisterForm } from './RegisterForm';
import { useAuth } from '../../hooks/useAuth';

export function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const { login, register, isLoading, error, clearError } = useAuth();

  const handleLogin = useCallback(async (email: string, password: string) => {
    const success = await login(email, password);
    if (success) {
      window.location.reload();
    }
  }, [login]);

  const handleRegister = useCallback(async (email: string, password: string, username: string) => {
    const success = await register(email, password, username);
    if (success) {
      window.location.reload();
    }
  }, [register]);

  const handleToggleForm = useCallback(() => {
    clearError();
    setIsLogin(prev => !prev);
  }, [clearError]);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h1 className="text-center text-3xl font-extrabold text-gray-900 mb-8">
          GymTracker
        </h1>
        {error && (
          <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
            {error}
          </div>
        )}
      </div>

      {isLogin ? (
        <LoginForm 
          onSubmit={handleLogin} 
          onToggleForm={handleToggleForm}
          isLoading={isLoading}
        />
      ) : (
        <RegisterForm 
          onSubmit={handleRegister} 
          onToggleForm={handleToggleForm}
          isLoading={isLoading}
        />
      )}
    </div>
  );
}