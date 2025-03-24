import { AxiosError } from 'axios';

export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
    Object.setPrototypeOf(this, ApiError.prototype);
  }
}

export function handleApiError(error: AxiosError): ApiError {
  if (error.response) {
    const statusCode = error.response.status;
    const detail = error.response.data?.detail;
    
    // Handle specific error cases
    if (statusCode === 401) {
      return new ApiError('Invalid email or password', statusCode);
    }
    if (statusCode === 400 && detail?.includes('Email already registered')) {
      return new ApiError('This email is already registered', statusCode);
    }
    
    return new ApiError(detail || 'An error occurred', statusCode);
  }
  
  if (error.request) {
    return new ApiError('Unable to connect to the server');
  }
  
  return new ApiError('An unexpected error occurred');
}