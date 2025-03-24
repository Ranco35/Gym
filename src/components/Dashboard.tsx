import React from 'react';
import { Activity, TrendingUp, Calendar, Clock as ClockIcon, ArrowRight, Dumbbell, LayoutDashboard, BarChart } from 'lucide-react';

// Componente para la página principal (Dashboard)
export function Dashboard() {
  // Datos del próximo entrenamiento
  const nextWorkout = {
    name: 'Pecho y Hombros',
    day: 'Lunes',
    exercises: 8,
    mainMuscles: ['Pectorales', 'Deltoides', 'Tríceps']
  };
  
  // Datos de ejercicios recientes
  const recentExercises = [
    { id: '1', name: 'Press de Banca', weight: 85, reps: '8, 8, 7, 6', date: 'Hace 2 días' },
    { id: '2', name: 'Sentadilla', weight: 140, reps: '10, 10, 8', date: 'Hace 3 días' },
    { id: '3', name: 'Peso Muerto', weight: 160, reps: '6, 6, 5', date: 'Hace 5 días' },
  ];
  
  // Datos de progreso semanal
  const weeklyStats = {
    workouts: 4,
    volume: '14,520 kg',
    duration: '4h 15m',
    progress: '+5%'
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">¡Bienvenido a GymTracker!</h1>
      
      {/* Sección del próximo entrenamiento */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Próximo Entrenamiento</h2>
            <span className="bg-blue-100 text-blue-800 rounded-full px-3 py-1 text-sm font-medium">
              {nextWorkout.day}
            </span>
          </div>
          
          <h3 className="text-xl font-bold text-gray-900 mb-2">{nextWorkout.name}</h3>
          
          <div className="flex items-center text-sm text-gray-600 mb-4">
            <Dumbbell className="h-4 w-4 mr-1" />
            <span>{nextWorkout.exercises} ejercicios planificados</span>
          </div>
          
          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-2">Grupos musculares principales:</p>
            <div className="flex flex-wrap gap-2">
              {nextWorkout.mainMuscles.map((muscle, index) => (
                <span 
                  key={index}
                  className="bg-gray-100 text-gray-800 text-xs px-2.5 py-1 rounded-full"
                >
                  {muscle}
                </span>
              ))}
            </div>
          </div>
          
          <button
            className="w-full flex justify-center items-center bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md"
          >
            Comenzar Entrenamiento <ArrowRight className="ml-2 h-4 w-4" />
          </button>
        </div>
      </div>
      
      {/* Grid de accesos directos */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <QuickAccessCard 
          icon={<LayoutDashboard className="h-6 w-6 text-blue-500" />}
          title="Crear Rutina"
          description="Diseña tu rutina personalizada"
          linkText="Ir a Rutinas"
          route="routine"
        />
        <QuickAccessCard 
          icon={<Calendar className="h-6 w-6 text-green-500" />}
          title="Entrenar"
          description="Registra tu próximo entrenamiento"
          linkText="Ver Rutinas"
          route="workout"
        />
        <QuickAccessCard 
          icon={<BarChart className="h-6 w-6 text-purple-500" />}
          title="Progreso"
          description="Visualiza tus avances"
          linkText="Ver Estadísticas"
          route="progress"
        />
        <QuickAccessCard 
          icon={<Dumbbell className="h-6 w-6 text-orange-500" />}
          title="Ejercicios"
          description="Explora la biblioteca de ejercicios"
          linkText="Ver Ejercicios"
          route="exercises"
        />
      </div>
      
      {/* Últimos entrenamientos y estadísticas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ejercicios recientes */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Ejercicios Recientes</h2>
            <div className="space-y-4">
              {recentExercises.map(exercise => (
                <div key={exercise.id} className="flex justify-between items-start pb-3 border-b border-gray-200">
                  <div>
                    <h3 className="font-medium text-gray-900">{exercise.name}</h3>
                    <p className="text-sm text-gray-500">
                      {exercise.weight} kg • {exercise.reps} reps
                    </p>
                  </div>
                  <span className="text-xs text-gray-500">{exercise.date}</span>
                </div>
              ))}
            </div>
            <div className="mt-4 text-center">
              <a href="#" className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                Ver historial completo
              </a>
            </div>
          </div>
        </div>
        
        {/* Estadísticas semanales */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Estadísticas de la Semana</h2>
            <div className="grid grid-cols-2 gap-4">
              <StatItem 
                icon={<Calendar className="h-5 w-5 text-blue-500" />}
                label="Entrenamientos"
                value={weeklyStats.workouts}
              />
              <StatItem 
                icon={<BarChart className="h-5 w-5 text-green-500" />}
                label="Volumen total"
                value={weeklyStats.volume}
              />
              <StatItem 
                icon={<ClockIcon className="h-5 w-5 text-purple-500" />}
                label="Tiempo total"
                value={weeklyStats.duration}
              />
              <StatItem 
                icon={<TrendingUp className="h-5 w-5 text-orange-500" />}
                label="Progreso"
                value={weeklyStats.progress}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

interface QuickAccessCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  linkText: string;
  route: string;
}

function QuickAccessCard({ icon, title, description, linkText, route }: QuickAccessCardProps) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="mb-3">{icon}</div>
      <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
      <p className="text-sm text-gray-600 mb-3">{description}</p>
      <a 
        href={`#${route}`}
        className="text-sm text-blue-600 hover:text-blue-800 font-medium flex items-center"
      >
        {linkText} <ArrowRight className="ml-1 h-3 w-3" />
      </a>
    </div>
  );
}

interface StatItemProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
}

function StatItem({ icon, label, value }: StatItemProps) {
  return (
    <div className="flex items-center p-3 bg-gray-50 rounded-lg">
      <div className="mr-3">{icon}</div>
      <div>
        <p className="text-xs text-gray-500">{label}</p>
        <p className="font-semibold text-gray-900">{value}</p>
      </div>
    </div>
  );
}