import React, { useState } from 'react';
import { Home, Dumbbell, Calendar, BarChart3, Library, User, LogOut } from 'lucide-react';
import { Dashboard } from './Dashboard';
import { WorkoutCreator } from './WorkoutCreator';
import { WorkoutExecutor } from './WorkoutExecutor';
import { ProgressTracker } from './ProgressTracker';
import { ExerciseLibrary } from './ExerciseLibrary';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  // Estado para controlar la pestaña activa
  const [activeTab, setActiveTab] = useState('home');

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
      default:
        return children;
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-lg font-bold text-gray-900">GymTracker</h1>
          <button 
            onClick={handleLogout}
            className="flex items-center text-gray-600 hover:text-red-600"
          >
            <LogOut size={16} className="mr-1" />
            <span className="text-sm">Cerrar sesión</span>
          </button>
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