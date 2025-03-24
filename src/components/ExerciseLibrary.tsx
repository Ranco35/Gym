import React, { useState } from 'react';
import { Search, Filter, ChevronDown, ChevronUp, Info } from 'lucide-react';

// Tipos de datos
interface Exercise {
  id: string;
  name: string;
  category: 'pecho' | 'espalda' | 'piernas' | 'hombros' | 'brazos' | 'core' | 'otro';
  equipment: 'barra' | 'mancuernas' | 'máquina' | 'cables' | 'peso corporal' | 'otro';
  mainMuscles: string[];
  secondaryMuscles: string[];
  description: string;
  instructions: string[];
  videoUrl?: string;
  isFavorite: boolean;
}

export function ExerciseLibrary() {
  // Estado para los ejercicios (simulando base de datos)
  const [exercises, setExercises] = useState<Exercise[]>([
    {
      id: '1',
      name: 'Press de Banca',
      category: 'pecho',
      equipment: 'barra',
      mainMuscles: ['Pectorales', 'Tríceps'],
      secondaryMuscles: ['Deltoides anteriores'],
      description: 'Ejercicio compuesto para el desarrollo del pecho y tríceps',
      instructions: [
        'Acuéstate en un banco plano con los pies apoyados en el suelo',
        'Agarra la barra con las manos un poco más separadas que el ancho de los hombros',
        'Baja la barra hasta tocar ligeramente el pecho',
        'Empuja la barra hacia arriba hasta extender los brazos'
      ],
      videoUrl: 'https://www.youtube.com/watch?v=rT7DgCr-3pg',
      isFavorite: true
    },
    {
      id: '2',
      name: 'Sentadilla',
      category: 'piernas',
      equipment: 'barra',
      mainMuscles: ['Cuádriceps', 'Glúteos'],
      secondaryMuscles: ['Isquiotibiales', 'Aductores', 'Pantorrillas'],
      description: 'Ejercicio fundamental para el desarrollo de la fuerza y masa en las piernas',
      instructions: [
        'Coloca la barra en la parte superior de los trapecios',
        'Separa los pies al ancho de los hombros',
        'Desciende flexionando las rodillas y caderas hasta que los muslos estén paralelos al suelo',
        'Mantén la espalda recta durante todo el movimiento',
        'Empuja a través de los talones para volver a la posición inicial'
      ],
      videoUrl: 'https://www.youtube.com/watch?v=bEv6CCg2BC8',
      isFavorite: true
    },
    {
      id: '3',
      name: 'Peso Muerto',
      category: 'espalda',
      equipment: 'barra',
      mainMuscles: ['Espalda baja', 'Isquiotibiales', 'Glúteos'],
      secondaryMuscles: ['Trapecios', 'Antebrazos', 'Cuádriceps'],
      description: 'Uno de los ejercicios más completos para desarrollar fuerza en todo el cuerpo',
      instructions: [
        'Colócate frente a la barra con los pies separados al ancho de las caderas',
        'Flexiona las rodillas y caderas para agarrar la barra con las manos a la anchura de los hombros',
        'Mantén la espalda recta y el pecho hacia arriba',
        'Levanta la barra extendiendo las caderas y rodillas',
        'Baja la barra controlando el movimiento'
      ],
      videoUrl: 'https://www.youtube.com/watch?v=ytGaGIn3SjE',
      isFavorite: false
    },
    {
      id: '4',
      name: 'Press Militar',
      category: 'hombros',
      equipment: 'barra',
      mainMuscles: ['Deltoides', 'Trapecio'],
      secondaryMuscles: ['Tríceps', 'Deltoides anteriores'],
      description: 'Ejercicio compuesto para el desarrollo de los hombros',
      instructions: [
        'Mantente de pie con la barra apoyada en la parte delantera de los hombros',
        'Agarra la barra con las manos un poco más anchas que los hombros',
        'Empuja la barra hacia arriba hasta extender completamente los brazos',
        'Baja la barra de forma controlada hasta la posición inicial'
      ],
      videoUrl: 'https://www.youtube.com/watch?v=2yjwXTZQDDI',
      isFavorite: false
    },
    {
      id: '5',
      name: 'Dominadas',
      category: 'espalda',
      equipment: 'peso corporal',
      mainMuscles: ['Dorsal ancho', 'Bíceps'],
      secondaryMuscles: ['Romboides', 'Trapecio medio'],
      description: 'Excelente ejercicio para el desarrollo de la espalda superior',
      instructions: [
        'Agarra la barra con las palmas mirando hacia adelante',
        'Cuelga con los brazos totalmente extendidos',
        'Tira de tu cuerpo hacia arriba hasta que la barbilla supere la barra',
        'Baja controladamente hasta la posición inicial'
      ],
      videoUrl: 'https://www.youtube.com/watch?v=eGo4IYlbE5g',
      isFavorite: true
    }
  ]);

  // Estados para filtros y búsqueda
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    category: '',
    equipment: '',
    favorites: false
  });
  const [showFilters, setShowFilters] = useState(false);
  const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null);

  // Filtrar ejercicios basados en la búsqueda y filtros
  const filteredExercises = exercises.filter(exercise => {
    // Filtro por término de búsqueda
    const matchesSearch = exercise.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          exercise.description.toLowerCase().includes(searchQuery.toLowerCase());
    
    // Filtro por categoría
    const matchesCategory = filters.category === '' || exercise.category === filters.category;
    
    // Filtro por equipamiento
    const matchesEquipment = filters.equipment === '' || exercise.equipment === filters.equipment;
    
    // Filtro por favoritos
    const matchesFavorites = !filters.favorites || exercise.isFavorite;
    
    return matchesSearch && matchesCategory && matchesEquipment && matchesFavorites;
  });

  // Función para alternar favoritos
  const toggleFavorite = (id: string) => {
    setExercises(exercises.map(ex => 
      ex.id === id ? { ...ex, isFavorite: !ex.isFavorite } : ex
    ));
  };

  // Mostrar detalles de un ejercicio
  const showExerciseDetails = (exercise: Exercise) => {
    setSelectedExercise(exercise);
  };

  // Cerrar modal de detalles
  const closeExerciseDetails = () => {
    setSelectedExercise(null);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Biblioteca de Ejercicios</h1>
      
      {/* Barra de búsqueda */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          placeholder="Buscar ejercicios..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        />
      </div>
      
      {/* Botón de filtros */}
      <div className="flex justify-between items-center">
        <button
          className="flex items-center space-x-2 text-gray-700 hover:text-gray-900"
          onClick={() => setShowFilters(!showFilters)}
        >
          <Filter className="h-5 w-5" />
          <span>Filtros</span>
          {showFilters ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </button>
        
        <span className="text-sm text-gray-500">
          {filteredExercises.length} ejercicios encontrados
        </span>
      </div>
      
      {/* Panel de filtros */}
      {showFilters && (
        <div className="bg-gray-50 p-4 rounded-md border border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Categoría
              </label>
              <select
                value={filters.category}
                onChange={(e) => setFilters({ ...filters, category: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="">Todas las categorías</option>
                <option value="pecho">Pecho</option>
                <option value="espalda">Espalda</option>
                <option value="piernas">Piernas</option>
                <option value="hombros">Hombros</option>
                <option value="brazos">Brazos</option>
                <option value="core">Core</option>
                <option value="otro">Otro</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Equipamiento
              </label>
              <select
                value={filters.equipment}
                onChange={(e) => setFilters({ ...filters, equipment: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="">Todo el equipamiento</option>
                <option value="barra">Barra</option>
                <option value="mancuernas">Mancuernas</option>
                <option value="máquina">Máquina</option>
                <option value="cables">Cables</option>
                <option value="peso corporal">Peso corporal</option>
                <option value="otro">Otro</option>
              </select>
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="favorites"
                checked={filters.favorites}
                onChange={(e) => setFilters({ ...filters, favorites: e.target.checked })}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 rounded"
              />
              <label htmlFor="favorites" className="ml-2 block text-sm text-gray-700">
                Solo favoritos
              </label>
            </div>
          </div>
          <div className="mt-4 flex justify-end">
            <button
              onClick={() => setFilters({ category: '', equipment: '', favorites: false })}
              className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900"
            >
              Restablecer filtros
            </button>
          </div>
        </div>
      )}
      
      {/* Lista de ejercicios */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredExercises.map(exercise => (
          <div 
            key={exercise.id} 
            className="bg-white rounded-lg shadow overflow-hidden cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => showExerciseDetails(exercise)}
          >
            <div className="p-4">
              <div className="flex justify-between items-start">
                <h3 className="text-lg font-medium text-gray-900">{exercise.name}</h3>
                <button 
                  className={`p-1 rounded-full ${exercise.isFavorite ? 'text-yellow-500' : 'text-gray-300'}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleFavorite(exercise.id);
                  }}
                >
                  <svg className="h-5 w-5 fill-current" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                </button>
              </div>
              <div className="flex space-x-2 mt-2">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {exercise.category}
                </span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  {exercise.equipment}
                </span>
              </div>
              <p className="mt-2 text-sm text-gray-500">{exercise.description}</p>
            </div>
          </div>
        ))}
      </div>
      
      {/* Si no hay resultados */}
      {filteredExercises.length === 0 && (
        <div className="bg-white rounded-lg shadow p-6 text-center">
          <p className="text-gray-500">No se encontraron ejercicios con los criterios seleccionados.</p>
          <button
            onClick={() => {
              setSearchQuery('');
              setFilters({ category: '', equipment: '', favorites: false });
            }}
            className="mt-2 text-blue-600 hover:text-blue-800"
          >
            Eliminar filtros
          </button>
        </div>
      )}
      
      {/* Modal de detalles de ejercicio */}
      {selectedExercise && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-xl font-bold text-gray-900">{selectedExercise.name}</h2>
                <button
                  onClick={closeExerciseDetails}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="flex flex-wrap gap-2 mb-4">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {selectedExercise.category}
                </span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  {selectedExercise.equipment}
                </span>
              </div>
              
              <p className="text-gray-700 mb-4">{selectedExercise.description}</p>
              
              <div className="mb-4">
                <h3 className="text-lg font-medium text-gray-900 mb-2">Músculos principales</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedExercise.mainMuscles.map((muscle, index) => (
                    <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      {muscle}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="mb-4">
                <h3 className="text-lg font-medium text-gray-900 mb-2">Músculos secundarios</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedExercise.secondaryMuscles.map((muscle, index) => (
                    <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                      {muscle}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="mb-4">
                <h3 className="text-lg font-medium text-gray-900 mb-2">Instrucciones</h3>
                <ol className="list-decimal pl-5 space-y-1">
                  {selectedExercise.instructions.map((instruction, index) => (
                    <li key={index} className="text-gray-700">{instruction}</li>
                  ))}
                </ol>
              </div>
              
              {selectedExercise.videoUrl && (
                <div className="mt-4">
                  <a 
                    href={selectedExercise.videoUrl} 
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-blue-600 hover:text-blue-800"
                  >
                    <Info className="h-4 w-4 mr-1" />
                    Ver video tutorial
                  </a>
                </div>
              )}
            </div>
            
            <div className="bg-gray-50 px-6 py-4 flex justify-end">
              <button
                onClick={closeExerciseDetails}
                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-md text-gray-700"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 