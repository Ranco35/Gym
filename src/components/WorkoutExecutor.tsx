import React, { useState } from 'react';
import { CheckCircle, ChevronDown, ChevronUp } from 'lucide-react';

// Tipos de datos
interface ExerciseSet {
  id: string;
  weight: number;
  reps: number;
  completed: boolean;
}

interface WorkoutExercise {
  id: string;
  name: string;
  targetSets: number;
  targetReps: string;
  suggestedWeight: number;
  notes?: string;
  sets: ExerciseSet[];
  expanded: boolean;
}

export function WorkoutExecutor() {
  // Estado para el entrenamiento actual
  const [currentWorkout, setCurrentWorkout] = useState({
    id: '1',
    name: 'Pecho y Hombros',
    day: 'Lunes',
    exercises: [
      {
        id: '1',
        name: 'Press de Banca',
        targetSets: 4,
        targetReps: '8-10',
        suggestedWeight: 80,
        notes: 'Mantener escápulas retraídas',
        sets: [
          { id: '1-1', weight: 80, reps: 0, completed: false },
          { id: '1-2', weight: 80, reps: 0, completed: false },
          { id: '1-3', weight: 80, reps: 0, completed: false },
          { id: '1-4', weight: 80, reps: 0, completed: false }
        ],
        expanded: true
      },
      {
        id: '2',
        name: 'Press de Hombros',
        targetSets: 3,
        targetReps: '10-12',
        suggestedWeight: 50,
        notes: 'Evitar arquear la espalda',
        sets: [
          { id: '2-1', weight: 50, reps: 0, completed: false },
          { id: '2-2', weight: 50, reps: 0, completed: false },
          { id: '2-3', weight: 50, reps: 0, completed: false }
        ],
        expanded: false
      },
      {
        id: '3',
        name: 'Aperturas con Mancuernas',
        targetSets: 3,
        targetReps: '12-15',
        suggestedWeight: 20,
        sets: [
          { id: '3-1', weight: 20, reps: 0, completed: false },
          { id: '3-2', weight: 20, reps: 0, completed: false },
          { id: '3-3', weight: 20, reps: 0, completed: false }
        ],
        expanded: false
      }
    ],
    startTime: new Date(),
    inProgress: true
  });

  // Cálculo de progreso
  const totalSets = currentWorkout.exercises.reduce((acc, ex) => acc + ex.sets.length, 0);
  const completedSets = currentWorkout.exercises.reduce(
    (acc, ex) => acc + ex.sets.filter(set => set.completed).length, 
    0
  );
  const progressPercentage = Math.round((completedSets / totalSets) * 100);

  // Función para actualizar el peso de un set
  const updateSetWeight = (exerciseId: string, setId: string, weight: number) => {
    setCurrentWorkout(workout => ({
      ...workout,
      exercises: workout.exercises.map(ex => 
        ex.id === exerciseId
          ? {
              ...ex,
              sets: ex.sets.map(set => 
                set.id === setId
                  ? { ...set, weight }
                  : set
              )
            }
          : ex
      )
    }));
  };

  // Función para actualizar las repeticiones de un set
  const updateSetReps = (exerciseId: string, setId: string, reps: number) => {
    setCurrentWorkout(workout => ({
      ...workout,
      exercises: workout.exercises.map(ex => 
        ex.id === exerciseId
          ? {
              ...ex,
              sets: ex.sets.map(set => 
                set.id === setId
                  ? { ...set, reps }
                  : set
              )
            }
          : ex
      )
    }));
  };

  // Función para marcar un set como completado
  const toggleSetCompleted = (exerciseId: string, setId: string) => {
    setCurrentWorkout(workout => ({
      ...workout,
      exercises: workout.exercises.map(ex => 
        ex.id === exerciseId
          ? {
              ...ex,
              sets: ex.sets.map(set => 
                set.id === setId
                  ? { ...set, completed: !set.completed }
                  : set
              )
            }
          : ex
      )
    }));
  };

  // Función para expandir/colapsar un ejercicio
  const toggleExerciseExpanded = (exerciseId: string) => {
    setCurrentWorkout(workout => ({
      ...workout,
      exercises: workout.exercises.map(ex => 
        ex.id === exerciseId
          ? { ...ex, expanded: !ex.expanded }
          : ex
      )
    }));
  };

  // Función para finalizar el entrenamiento
  const finishWorkout = () => {
    // Aquí implementarías la lógica para guardar el entrenamiento
    console.log('Finalizando entrenamiento:', currentWorkout);
    
    // Calcular duración
    const duration = Math.round((new Date().getTime() - currentWorkout.startTime.getTime()) / 60000);
    alert(`Entrenamiento finalizado. Duración: ${duration} minutos`);
    
    setCurrentWorkout(workout => ({
      ...workout,
      inProgress: false,
      endTime: new Date()
    }));
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">{currentWorkout.name}</h1>
        <span className="bg-blue-100 text-blue-800 rounded-full px-3 py-1 text-sm font-medium">
          {currentWorkout.day}
        </span>
      </div>
      
      {/* Barra de progreso */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Progreso del entrenamiento</span>
          <span className="text-sm font-medium text-blue-600">{progressPercentage}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div 
            className="bg-blue-600 h-2.5 rounded-full" 
            style={{ width: `${progressPercentage}%` }}
          ></div>
        </div>
        <div className="mt-2 text-xs text-gray-500 text-center">
          {completedSets} de {totalSets} series completadas
        </div>
      </div>
      
      {/* Lista de ejercicios */}
      <div className="space-y-4">
        {currentWorkout.exercises.map(exercise => (
          <div key={exercise.id} className="bg-white rounded-lg shadow overflow-hidden">
            <div 
              className="p-4 flex justify-between items-center cursor-pointer"
              onClick={() => toggleExerciseExpanded(exercise.id)}
            >
              <div>
                <h3 className="font-medium text-gray-900">{exercise.name}</h3>
                <p className="text-sm text-gray-600">
                  {exercise.targetSets} series × {exercise.targetReps} reps
                </p>
              </div>
              <div className="flex items-center">
                <span className="text-sm mr-2">
                  {exercise.sets.filter(s => s.completed).length}/{exercise.sets.length}
                </span>
                {exercise.expanded ? (
                  <ChevronUp className="h-5 w-5 text-gray-500" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-gray-500" />
                )}
              </div>
            </div>
            
            {exercise.expanded && (
              <div className="border-t border-gray-200 p-4">
                {exercise.notes && (
                  <div className="mb-4 bg-yellow-50 p-3 rounded-md text-sm text-yellow-800">
                    <p className="font-medium">Notas:</p>
                    <p>{exercise.notes}</p>
                  </div>
                )}
                
                <div className="space-y-3">
                  <div className="grid grid-cols-12 gap-2 text-xs font-medium text-gray-700 border-b pb-2">
                    <div className="col-span-1">Set</div>
                    <div className="col-span-4">Peso (kg)</div>
                    <div className="col-span-4">Reps</div>
                    <div className="col-span-3 text-center">Completado</div>
                  </div>
                  
                  {exercise.sets.map((set, index) => (
                    <div key={set.id} className="grid grid-cols-12 gap-2 items-center">
                      <div className="col-span-1 text-sm font-medium">{index + 1}</div>
                      <div className="col-span-4">
                        <div className="flex items-center">
                          <button 
                            className="text-gray-500 px-2 py-1 rounded-l-md border border-gray-300"
                            onClick={() => updateSetWeight(exercise.id, set.id, Math.max(0, set.weight - 2.5))}
                          >
                            -
                          </button>
                          <input
                            type="number"
                            value={set.weight}
                            onChange={(e) => updateSetWeight(exercise.id, set.id, parseFloat(e.target.value) || 0)}
                            className="w-full text-center border-t border-b border-gray-300 py-1 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                            step="2.5"
                          />
                          <button 
                            className="text-gray-500 px-2 py-1 rounded-r-md border border-gray-300"
                            onClick={() => updateSetWeight(exercise.id, set.id, set.weight + 2.5)}
                          >
                            +
                          </button>
                        </div>
                      </div>
                      <div className="col-span-4">
                        <div className="flex items-center">
                          <button 
                            className="text-gray-500 px-2 py-1 rounded-l-md border border-gray-300"
                            onClick={() => updateSetReps(exercise.id, set.id, Math.max(0, set.reps - 1))}
                          >
                            -
                          </button>
                          <input
                            type="number"
                            value={set.reps}
                            onChange={(e) => updateSetReps(exercise.id, set.id, parseInt(e.target.value) || 0)}
                            className="w-full text-center border-t border-b border-gray-300 py-1 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          />
                          <button 
                            className="text-gray-500 px-2 py-1 rounded-r-md border border-gray-300"
                            onClick={() => updateSetReps(exercise.id, set.id, set.reps + 1)}
                          >
                            +
                          </button>
                        </div>
                      </div>
                      <div className="col-span-3 text-center">
                        <button
                          onClick={() => toggleSetCompleted(exercise.id, set.id)}
                          className={`w-8 h-8 rounded-full flex items-center justify-center ${
                            set.completed
                              ? 'bg-green-100 text-green-600'
                              : 'bg-gray-100 text-gray-400'
                          }`}
                        >
                          <CheckCircle className="h-5 w-5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
      
      {/* Botón de finalizar */}
      <button
        onClick={finishWorkout}
        className="w-full py-3 px-4 bg-green-600 text-white rounded-md hover:bg-green-700"
      >
        Finalizar entrenamiento
      </button>
    </div>
  );
} 