import axios from 'axios';
import { handleApiError } from '../utils/errorHandling';

// URL base de la API Django
const API_URL = 'http://127.0.0.1:8000';

// Función para obtener el token CSRF
const getCsrfToken = async () => {
  try {
    const response = await axios.get(`${API_URL}/auth/csrf/`);
    return response.data.csrfToken;
  } catch (error) {
    console.error('Error al obtener token CSRF:', error);
    return null;
  }
};

// Crear una instancia de Axios configurada
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Asegura el envío de cookies como CSRF o sesión
});

// Interceptor para añadir el token de autenticación en las solicitudes
api.interceptors.request.use(async (config) => {
  // Añadir token de autenticación si existe
  const token = localStorage.getItem('auth_token'); // Token JWT almacenado
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  // Para las rutas que no necesitan CSRF, simplemente devolvemos la configuración
  if (
    config.url?.includes('/auth/login') ||
    config.url?.includes('/auth/api-token') ||
    config.url?.includes('/auth/register')
  ) {
    // Para rutas de autenticación, no es necesario el token CSRF
    return config;
  }
  
  // Para otras rutas, intentamos añadir token CSRF
  try {
    const csrfToken = await getCsrfToken();
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
  } catch (error) {
    console.error('Error al obtener token CSRF:', error);
  }
  
  return config;
});

// Manejo de respuestas e integración de errores
api.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(handleApiError(error))
);

// Función para registrar usuarios
export const registerUser = async (userData: { username: string; email: string; password: string }) => {
  try {
    const response = await api.post('/auth/register', userData);
    // Guardar el token si se incluye en la respuesta
    if (response.data.access) {
      localStorage.setItem('auth_token', response.data.access);
    }
    return response.data;
  } catch (error: any) {
    console.error('Error al registrar usuario:', error.response?.data || error.message);
    throw error;
  }
};

// Función para login de usuarios
export const loginUser = async (credentials: { username: string; password: string }) => {
  try {
    const response = await api.post('/auth/api-token/', credentials);
    if (response.data.access) {
      localStorage.setItem('auth_token', response.data.access);
    }
    return response.data;
  } catch (error: any) {
    console.error('Error al iniciar sesión:', error.response?.data || error.message);
    throw error;
  }
};

// Función para obtener el perfil del usuario autenticado
export const getUserProfile = async () => {
  try {
    const response = await api.get('/auth/profile');
    return response.data;
  } catch (error: any) {
    console.error('Error al obtener perfil del usuario:', error.response?.data || error.message);
    throw error;
  }
};

// Función para guardar una rutina de entrenamiento 
export const saveWorkout = async (workoutData: any) => {
  try {
    const response = await api.post('/api/workouts/', workoutData);
    return response.data;
  } catch (error: any) {
    console.error('Error al guardar rutina:', error.response?.data || error.message);
    throw error;
  }
};

// Función para obtener todas las rutinas
export const getWorkouts = async () => {
  try {
    const response = await api.get('/api/workouts/');
    return response.data;
  } catch (error: any) {
    console.error('Error al obtener rutinas:', error.response?.data || error.message);
    throw error;
  }
};

// Función para obtener una rutina específica
export const getWorkout = async (id: string) => {
  try {
    const response = await api.get(`/api/workouts/${id}/`);
    return response.data;
  } catch (error: any) {
    console.error('Error al obtener rutina:', error.response?.data || error.message);
    throw error;
  }
};

// Función para actualizar una rutina existente
export const updateWorkout = async (id: string, workoutData: any) => {
  try {
    const response = await api.put(`/api/workouts/${id}/`, workoutData);
    return response.data;
  } catch (error: any) {
    console.error('Error al actualizar rutina:', error.response?.data || error.message);
    throw error;
  }
};

// Función para eliminar una rutina
export const deleteWorkout = async (id: string) => {
  try {
    await api.delete(`/api/workouts/${id}/`);
    return true;
  } catch (error: any) {
    console.error('Error al eliminar rutina:', error.response?.data || error.message);
    throw error;
  }
};

// Funciones para las sesiones de entrenamiento
export const saveTraining = async (trainingData: any) => {
  try {
    const response = await api.post('/api/trainings/', trainingData);
    return response.data;
  } catch (error: any) {
    console.error('Error al guardar entrenamiento:', error.response?.data || error.message);
    throw error;
  }
};

export const getTrainings = async () => {
  try {
    const response = await api.get('/api/trainings/');
    return response.data;
  } catch (error: any) {
    console.error('Error al obtener entrenamientos:', error.response?.data || error.message);
    throw error;
  }
};
