import React, { useState, useEffect } from 'react';
import { Home, Dumbbell, Calendar, BarChart3, Library, User, LogOut, Users } from 'lucide-react';
import { Dashboard } from './Dashboard';
import { WorkoutCreator } from './WorkoutCreator';
import { WorkoutExecutor } from './WorkoutExecutor';
import { ProgressTracker } from './ProgressTracker';
import { ExerciseLibrary } from './ExerciseLibrary';
import { UserAdmin } from './UserAdmin';

interface LayoutProps {
  children: React.ReactNode;
}

interface UserInfo {
  id: number;
  username: string;
  email: string;
  role: string;
  is_superuser: boolean;
}

export function Layout({ children }: LayoutProps) {
  // Estado para controlar la pestaña activa
  const [activeTab, setActiveTab] = useState('home');
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Obtener información del usuario al cargar
  useEffect(() => {
    const fetchUserInfo = async () => {
      try {
        const response = await fetch('/api/user/', { credentials: 'include' });
        if (response.ok) {
          const data = await response.json();
          setUserInfo(data);
        }
      } catch (error) {
        console.error('Error al obtener información del usuario:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchUserInfo();
  }, []);

  // Manejar cambio de tab
  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    console.log('Cambiando a:', tab);
  };

  // Función para cerrar sesión
  const handleLogout = () => {
    window.location.href = '/accounts/logout/';
  };

  // Renderizar el contenido correspondiente a la pestaña activa
  const renderContent = () => {
    switch (activeTab) {
      case 'home':
        return children;
      case 'routine':
        return <WorkoutCreator />;
      case 'workout':
        return <WorkoutExecutor />;
      case 'progress':
        return <ProgressTracker />;
      case 'exercises':
        return <ExerciseLibrary />;
      case 'profile':
        return <div>Perfil (Próximamente)</div>;
      case 'admin':
        return <UserAdmin />;
      default:
        return children;
    }
  };

  // Es administrador si el rol del usuario es ADMIN o es superusuario
  const isAdmin = userInfo?.role === 'ADMIN' || userInfo?.is_superuser === true;

  return (
    <div className="flex flex-col min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-lg font-bold text-gray-900">GymTracker</h1>
          <div className="flex items-center gap-4">
            {userInfo && (
              <span className="text-sm text-gray-600">
                {userInfo.username} 
                {isAdmin && <span className="ml-1 text-xs font-medium text-blue-600">(Admin)</span>}
              </span>
            )}
            <button 
              onClick={handleLogout}
              className="flex items-center text-gray-600 hover:text-red-600"
            >
              <LogOut size={16} className="mr-1" />
              <span className="text-sm">Cerrar sesión</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow">
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {renderContent()}
        </div>
      </main>

      {/* Bottom Navigation */}
      <nav className="bg-white border-t border-gray-200 fixed inset-x-0 bottom-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between">
            <NavItem 
              icon={<Home />} 
              label="Inicio" 
              active={activeTab === 'home'} 
              onClick={() => handleTabChange('home')}
            />
            <NavItem 
              icon={<Dumbbell />} 
              label="Rutinas" 
              active={activeTab === 'routine'} 
              onClick={() => handleTabChange('routine')}
            />
            <NavItem 
              icon={<Calendar />} 
              label="Entrenar" 
              active={activeTab === 'workout'} 
              onClick={() => handleTabChange('workout')}
            />
            <NavItem 
              icon={<BarChart3 />} 
              label="Progreso" 
              active={activeTab === 'progress'} 
              onClick={() => handleTabChange('progress')}
            />
            <NavItem 
              icon={<Library />} 
              label="Ejercicios" 
              active={activeTab === 'exercises'} 
              onClick={() => handleTabChange('exercises')}
            />
            <NavItem 
              icon={<User />} 
              label="Perfil" 
              active={activeTab === 'profile'} 
              onClick={() => handleTabChange('profile')}
            />
            {isAdmin && (
              <NavItem 
                icon={<Users />} 
                label="Admin" 
                active={activeTab === 'admin'} 
                onClick={() => handleTabChange('admin')}
              />
            )}
          </div>
        </div>
      </nav>

      {/* Padding to avoid content being hidden by the fixed navbar */}
      <div className="h-16"></div>
    </div>
  );
}

interface NavItemProps {
  icon: React.ReactNode;
  label: string;
  active: boolean;
  onClick: () => void;
}

function NavItem({ icon, label, active, onClick }: NavItemProps) {
  return (
    <button
      className={`flex flex-col items-center justify-center py-2 w-full ${
        active ? 'text-blue-600' : 'text-gray-500 hover:text-gray-900'
      }`}
      onClick={onClick}
    >
      <div className="icon">{icon}</div>
      <span className="text-xs mt-1">{label}</span>
    </button>
  );
}