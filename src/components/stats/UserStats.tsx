import React from 'react';
import { LineChart, BarChart, Activity } from 'lucide-react';
import { WeightProgress } from './WeightProgress';
import { VolumeChart } from './VolumeChart';
import { WorkoutFrequency } from './WorkoutFrequency';

export function UserStats() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Mis Estadísticas</h2>
      
      {/* Tarjetas de resumen */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Peso Actual</p>
              <p className="text-2xl font-bold">75.5 kg</p>
            </div>
            <LineChart className="h-8 w-8 text-blue-500" />
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Entrenamientos</p>
              <p className="text-2xl font-bold">12 este mes</p>
            </div>
            <Activity className="h-8 w-8 text-green-500" />
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Volumen Total</p>
              <p className="text-2xl font-bold">2,450 kg</p>
            </div>
            <BarChart className="h-8 w-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Gráficos detallados */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <WeightProgress />
        <VolumeChart />
        <WorkoutFrequency />
      </div>
    </div>
  );
}