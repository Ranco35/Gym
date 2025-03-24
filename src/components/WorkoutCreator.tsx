import React, { useState, useEffect } from 'react';
import { Plus, Trash, ArrowUp, ArrowDown, Save } from 'lucide-react';
import { saveWorkout as apiSaveWorkout } from '../services/api';
import axios from 'axios';

// Tipos de datos
interface Exercise {
  id: string;
  name: string;
  sets: number;
  reps: string; // Puede ser "8-10" o "12"
  weight: number;
  notes?: string;
}

interface DatabaseExercise {
  id: number;
  name: string;
  category: string;
  description: string;
  difficulty: string;
}

interface Workout {
  id: string;
  name: string;
  day: 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday';
  exercises: Exercise[];
}

export function WorkoutCreator() {
  // Estado para los ejercicios disponibles en la base de datos
  const [availableExercises, setAvailableExercises] = useState<DatabaseExercise[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Cargar ejercicios al iniciar el componente
  useEffect(() => {
    const fetchExercises = async () => {
      setLoading(true);
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/exercises/');
        setAvailableExercises(response.data);
        setError(null);
      } catch (err) {
        console.error('Error al cargar ejercicios:', err);
        setError('No se pudieron cargar los ejercicios. Por favor, actualiza la página.');
      } finally {
        setLoading(false);
      }
    };

    fetchExercises();
  }, []);

  // Estado para la semana de entrenamiento
  const [weeklyWorkouts, setWeeklyWorkouts] = useState<Workout[]>([
    { id: '1', name: 'Pecho y Hombros', day: 'monday', exercises: [] },
    { id: '2', name: 'Espalda', day: 'tuesday', exercises: [] },
    { id: '3', name: 'Piernas', day: 'wednesday', exercises: [] },
    { id: '4', name: 'Brazos', day: 'thursday', exercises: [] },
    { id: '5', name: 'Full Body', day: 'friday', exercises: [] }
  ]);
  
  // Estado para el día seleccionado
  const [selectedDay, setSelectedDay] = useState<string>('monday');

  // Obtener la rutina del día seleccionado
  const currentWorkout = weeklyWorkouts.find(w => w.day === selectedDay);

  // Función para añadir un ejercicio
  const addExercise = () => {
    if (!currentWorkout || availableExercises.length === 0) return;
    
    // Tomamos el primer ejercicio disponible como predeterminado
    const defaultExercise = availableExercises[0];
    
    const newExercise: Exercise = {
      id: defaultExercise.id.toString(),
      name: defaultExercise.name,
      sets: 3,
      reps: '8-10',
      weight: 0
    };
    
    setWeeklyWorkouts(workouts => 
      workouts.map(workout => 
        workout.id === currentWorkout.id 
          ? { ...workout, exercises: [...workout.exercises, newExercise] }
          : workout
      )
    );
  };

  // Función para actualizar un ejercicio
  const updateExercise = (exerciseId: string, field: keyof Exercise, value: any) => {
    if (!currentWorkout) return;
    
    setWeeklyWorkouts(workouts => 
      workouts.map(workout => 
        workout.id === currentWorkout.id 
          ? { 
              ...workout, 
              exercises: workout.exercises.map(ex => 
                ex.id === exerciseId 
                  ? { ...ex, [field]: value }
                  : ex
              )
            }
          : workout
      )
    );
  };

  // Función para eliminar un ejercicio
  const removeExercise = (exerciseId: string) => {
    if (!currentWorkout) return;
    
    setWeeklyWorkouts(workouts => 
      workouts.map(workout => 
        workout.id === currentWorkout.id 
          ? { 
              ...workout, 
              exercises: workout.exercises.filter(ex => ex.id !== exerciseId) 
            }
          : workout
      )
    );
  };

  // Función para mover un ejercicio hacia arriba
  const moveExerciseUp = (index: number) => {
    if (!currentWorkout || index === 0) return;
    
    const newExercises = [...currentWorkout.exercises];
    [newExercises[index], newExercises[index - 1]] = [newExercises[index - 1], newExercises[index]];
    
    setWeeklyWorkouts(workouts => 
      workouts.map(workout => 
        workout.id === currentWorkout.id 
          ? { ...workout, exercises: newExercises }
          : workout
      )
    );
  };

  // Función para mover un ejercicio hacia abajo
  const moveExerciseDown = (index: number) => {
    if (!currentWorkout || index === currentWorkout.exercises.length - 1) return;
    
    const newExercises = [...currentWorkout.exercises];
    [newExercises[index], newExercises[index + 1]] = [newExercises[index + 1], newExercises[index]];
    
    setWeeklyWorkouts(workouts => 
      workouts.map(workout => 
        workout.id === currentWorkout.id 
          ? { ...workout, exercises: newExercises }
          : workout
      )
    );
  };

  // Función para guardar la rutina
  const saveWorkout = async () => {
    try {
      if (!currentWorkout) return;
      
      // Convertir los datos al formato esperado por el backend
      const workoutToSave = {
        name: currentWorkout.name,
        date: new Date().toISOString().split('T')[0], // Fecha actual en formato YYYY-MM-DD
        day_of_week: dayMapping[currentWorkout.day],
        exercises: currentWorkout.exercises.map(ex => ({
          exercise: ex.id, // ID del ejercicio (asumiendo que coincide con el ID del ejercicio en backend)
          sets: ex.sets,
          reps: ex.reps,
          weight: ex.weight,
          notes: ex.notes || ''
        }))
      };
      
      const result = await apiSaveWorkout(workoutToSave);
      console.log('Rutina guardada:', result);
      alert('Rutina guardada con éxito');
    } catch (error) {
      console.error('Error al guardar la rutina:', error);
      alert('Error al guardar la rutina. Por favor, inténtalo de nuevo.');
    }
  };

  // Mapeo de días en español
  const dayMapping: Record<string, string> = {
    'monday': 'Lunes',
    'tuesday': 'Martes',
    'wednesday': 'Miércoles',
    'thursday': 'Jueves',
    'friday': 'Viernes',
    'saturday': 'Sábado',
    'sunday': 'Domingo'
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Crear Rutina Semanal</h1>
      
      {/* Selector de días */}
      <div className="flex overflow-x-auto py-2 space-x-2">
        {weeklyWorkouts.map(workout => (
          <button
            key={workout.day}
            onClick={() => setSelectedDay(workout.day)}
            className={`px-4 py-2 rounded-md whitespace-nowrap ${
              selectedDay === workout.day
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {dayMapping[workout.day]}
          </button>
        ))}
      </div>
      
      {currentWorkout && (
        <>
          {/* Información de la rutina */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nombre de la rutina
              </label>
              <input
                type="text"
                value={currentWorkout.name}
                onChange={(e) => {
                  setWeeklyWorkouts(workouts =>
                    workouts.map(w =>
                      w.id === currentWorkout.id
                        ? { ...w, name: e.target.value }
                        : w
                    )
                  );
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Ej: Día de Pecho"
              />
            </div>
            
            {/* Lista de ejercicios */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-gray-900">Ejercicios</h2>
              
              {currentWorkout.exercises.length === 0 ? (
                <p className="text-gray-500 text-center py-4">
                  No hay ejercicios añadidos. Añade tu primer ejercicio.
                </p>
              ) : (
                <div className="space-y-4">
                  {currentWorkout.exercises.map((exercise, index) => (
                    <div key={exercise.id} className="bg-gray-50 p-4 rounded-md">
                      <div className="flex justify-between items-start mb-3">
                        <select
                          value={exercise.id}
                          onChange={(e) => {
                            const selectedExercise = availableExercises.find(ex => ex.id.toString() === e.target.value);
                            if (selectedExercise) {
                              updateExercise(exercise.id, 'id', selectedExercise.id.toString());
                              updateExercise(exercise.id, 'name', selectedExercise.name);
                            }
                          }}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        >
                          {availableExercises.map(ex => (
                            <option key={ex.id} value={ex.id}>
                              {ex.name} ({ex.category})
                            </option>
                          ))}
                        </select>
                        <div className="flex space-x-1 ml-2">
                          <button
                            onClick={() => moveExerciseUp(index)}
                            disabled={index === 0}
                            className={`p-1 rounded-md ${
                              index === 0 ? 'text-gray-400' : 'text-gray-600 hover:bg-gray-200'
                            }`}
                          >
                            <ArrowUp size={18} />
                          </button>
                          <button
                            onClick={() => moveExerciseDown(index)}
                            disabled={index === currentWorkout.exercises.length - 1}
                            className={`p-1 rounded-md ${
                              index === currentWorkout.exercises.length - 1
                                ? 'text-gray-400'
                                : 'text-gray-600 hover:bg-gray-200'
                            }`}
                          >
                            <ArrowDown size={18} />
                          </button>
                          <button
                            onClick={() => removeExercise(exercise.id)}
                            className="p-1 rounded-md text-red-600 hover:bg-red-100"
                          >
                            <Trash size={18} />
                          </button>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-3 gap-3">
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            Series
                          </label>
                          <input
                            type="number"
                            min="1"
                            value={exercise.sets}
                            onChange={(e) => updateExercise(exercise.id, 'sets', parseInt(e.target.value) || 0)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            Repeticiones
                          </label>
                          <input
                            type="text"
                            value={exercise.reps}
                            onChange={(e) => updateExercise(exercise.id, 'reps', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                            placeholder="Ej: 8-10 o 12"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            Peso (kg)
                          </label>
                          <input
                            type="number"
                            min="0"
                            step="2.5"
                            value={exercise.weight}
                            onChange={(e) => updateExercise(exercise.id, 'weight', parseFloat(e.target.value) || 0)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          />
                        </div>
                      </div>
                      
                      <div className="mt-3">
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                          Notas (opcional)
                        </label>
                        <textarea
                          value={exercise.notes || ''}
                          onChange={(e) => updateExercise(exercise.id, 'notes', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          rows={2}
                          placeholder="Instrucciones o notas para este ejercicio"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              <button
                onClick={addExercise}
                className="flex items-center justify-center w-full py-2 px-4 border border-dashed border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                <Plus size={16} className="mr-1" /> Añadir ejercicio
              </button>
            </div>
          </div>
          
          {/* Botón de guardar */}
          <button
            onClick={saveWorkout}
            className="flex items-center justify-center w-full py-3 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            <Save size={16} className="mr-2" /> Guardar rutina
          </button>
        </>
      )}
    </div>
  );
} 