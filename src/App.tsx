import React, { useState, useEffect } from 'react';
import { Layout } from './components/Layout';
import { Dashboard } from './components/Dashboard';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Verificar si estamos autenticados con sesión de Django
    const checkAuthSession = async () => {
      try {
        // Intentar acceder a un endpoint protegido
        const response = await fetch('/api/exercises/', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',  // Incluir cookies de sesión
        });
        
        if (response.ok) {
          // Si la respuesta es exitosa, estamos autenticados
          setIsAuthenticated(true);
          try {
            // Intenta obtener información del usuario
            const userResponse = await fetch('/api/user/', { 
              credentials: 'include' 
            });
            if (userResponse.ok) {
              const userData = await userResponse.json();
              setUser(userData);
            }
          } catch (error) {
            console.error('Error al obtener información del usuario:', error);
          }
        } else {
          // Si no estamos autenticados, redirigir inmediatamente a la página de login
          window.location.href = '/accounts/login/';
          return;
        }
      } catch (error) {
        console.error('Error al verificar autenticación:', error);
        // Si hay un error, redirigir a la página de login
        window.location.href = '/accounts/login/';
        return;
      } finally {
        setLoading(false);
      }
    };
    
    checkAuthSession();
  }, []);

  // Mostrar pantalla de carga mientras verificamos la autenticación
  if (loading) {
    return <div className="flex justify-center items-center h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p className="text-gray-600">Cargando...</p>
      </div>
    </div>;
  }

  // Si no está autenticado y ha terminado de cargar, redirigir a login
  if (!isAuthenticated) {
    window.location.href = '/accounts/login/';
    return null;
  }

  // Si está autenticado, mostrar el dashboard
  return (
    <Layout>
      <Dashboard />
    </Layout>
  );
}

export default App;