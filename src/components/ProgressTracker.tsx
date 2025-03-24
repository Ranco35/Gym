import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Calendar, TrendingUp, Dumbbell, Award } from 'lucide-react';

// Datos de ejemplo para las gráficas
const weeklyVolume = [
  { name: 'Sem 1', volume: 12000 },
  { name: 'Sem 2', volume: 13500 },
  { name: 'Sem 3', volume: 12800 },
  { name: 'Sem 4', volume: 14200 },
  { name: 'Sem 5', volume: 15000 },
  { name: 'Sem 6', volume: 14500 },
  { name: 'Sem 7', volume: 16200 },
  { name: 'Sem 8', volume: 16800 },
];

const exerciseProgress = [
  { date: '01/05', press: 80, squat: 120, deadlift: 150 },
  { date: '08/05', press: 82.5, squat: 125, deadlift: 155 },
  { date: '15/05', press: 85, squat: 130, deadlift: 160 },
  { date: '22/05', press: 85, squat: 135, deadlift: 165 },
  { date: '29/05', press: 87.5, squat: 140, deadlift: 170 },
  { date: '05/06', press: 90, squat: 142.5, deadlift: 175 },
];

// Tipos de datos
interface PersonalRecord {
  id: string;
  exercise: string;
  weight: number;
  reps: number;
  date: string;
}

export function ProgressTracker() {
  // Estado para el tipo de gráfica seleccionada
  const [selectedChart, setSelectedChart] = useState<'volume' | 'strength'>('volume');

  // Estado para filtros
  const [timeRange, setTimeRange] = useState<'8w' | '6m' | '1y'>('8w');
  
  // Datos de ejemplo para récords personales
  const personalRecords: PersonalRecord[] = [
    { id: '1', exercise: 'Press de Banca', weight: 100, reps: 1, date: '10/06/2023' },
    { id: '2', exercise: 'Sentadilla', weight: 150, reps: 1, date: '15/05/2023' },
    { id: '3', exercise: 'Peso Muerto', weight: 180, reps: 1, date: '20/04/2023' },
    { id: '4', exercise: 'Press Militar', weight: 70, reps: 1, date: '05/06/2023' },
    { id: '5', exercise: 'Dominadas', weight: 20, reps: 8, date: '01/06/2023' },
  ];
  
  // Datos de entrenamientos completados
  const workoutsSummary = {
    totalWorkouts: 47,
    thisMonth: 12,
    streak: 5,
    weeklyAverage: 3.5
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Tu Progreso</h1>
      
      {/* Resumen de entrenamientos */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard
          icon={<Calendar className="h-6 w-6 text-blue-500" />}
          label="Total Entrenamientos"
          value={workoutsSummary.totalWorkouts}
        />
        <StatCard
          icon={<TrendingUp className="h-6 w-6 text-green-500" />}
          label="Este Mes"
          value={workoutsSummary.thisMonth}
        />
        <StatCard
          icon={<Dumbbell className="h-6 w-6 text-purple-500" />}
          label="Racha Actual"
          value={`${workoutsSummary.streak} días`}
        />
        <StatCard
          icon={<Award className="h-6 w-6 text-orange-500" />}
          label="Promedio Semanal"
          value={workoutsSummary.weeklyAverage}
        />
      </div>
      
      {/* Selector de gráficas */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-6">
          <div className="space-x-2">
            <button
              onClick={() => setSelectedChart('volume')}
              className={`px-4 py-2 rounded-md ${
                selectedChart === 'volume'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Volumen de Entrenamiento
            </button>
            <button
              onClick={() => setSelectedChart('strength')}
              className={`px-4 py-2 rounded-md ${
                selectedChart === 'strength'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Progresión de Fuerza
            </button>
          </div>
          
          <div className="flex space-x-1">
            <button
              onClick={() => setTimeRange('8w')}
              className={`px-3 py-1 text-sm rounded-md ${
                timeRange === '8w'
                  ? 'bg-gray-700 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              8 sem
            </button>
            <button
              onClick={() => setTimeRange('6m')}
              className={`px-3 py-1 text-sm rounded-md ${
                timeRange === '6m'
                  ? 'bg-gray-700 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              6 meses
            </button>
            <button
              onClick={() => setTimeRange('1y')}
              className={`px-3 py-1 text-sm rounded-md ${
                timeRange === '1y'
                  ? 'bg-gray-700 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              1 año
            </button>
          </div>
        </div>
        
        {/* Gráfica de volumen */}
        {selectedChart === 'volume' && (
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={weeklyVolume}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => [`${value} kg`, 'Volumen']} />
                <Legend />
                <Bar dataKey="volume" name="Volumen (kg)" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
            <p className="text-center text-sm text-gray-500 mt-2">
              Volumen total levantado por semana (kg)
            </p>
          </div>
        )}
        
        {/* Gráfica de progreso por ejercicio */}
        {selectedChart === 'strength' && (
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={exerciseProgress}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value) => [`${value} kg`, '']} />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="press" 
                  name="Press de Banca" 
                  stroke="#3B82F6" 
                  activeDot={{ r: 8 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="squat" 
                  name="Sentadilla" 
                  stroke="#10B981" 
                  activeDot={{ r: 8 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="deadlift" 
                  name="Peso Muerto" 
                  stroke="#F59E0B" 
                  activeDot={{ r: 8 }}
                />
              </LineChart>
            </ResponsiveContainer>
            <p className="text-center text-sm text-gray-500 mt-2">
              Progresión del peso máximo utilizado en ejercicios clave
            </p>
          </div>
        )}
      </div>
      
      {/* Récords personales */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Récords Personales</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ejercicio</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Peso (kg)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Repeticiones</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {personalRecords.map((record) => (
                <tr key={record.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{record.exercise}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{record.weight}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{record.reps}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{record.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
}

function StatCard({ icon, label, value }: StatCardProps) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center space-x-3">
        {icon}
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className="text-lg font-semibold text-gray-900">{value}</p>
        </div>
      </div>
    </div>
  );
} 