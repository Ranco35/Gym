"""
Documentación de la API de Trainings
"""

# Trainings API
TRAINING_LIST_CREATE = {
    'get': {
        'description': 'Lista todos los entrenamientos del usuario autenticado',
        'parameters': [],
        'responses': {
            '200': 'Lista de entrenamientos',
            '401': 'No autenticado'
        }
    },
    'post': {
        'description': 'Crea un nuevo entrenamiento',
        'parameters': [
            {
                'name': 'name',
                'required': True,
                'type': 'string',
                'description': 'Nombre del entrenamiento'
            },
            {
                'name': 'date',
                'required': True,
                'type': 'date',
                'description': 'Fecha del entrenamiento (YYYY-MM-DD)'
            },
            {
                'name': 'notes',
                'required': False,
                'type': 'string',
                'description': 'Notas adicionales'
            }
        ],
        'responses': {
            '201': 'Entrenamiento creado',
            '400': 'Datos inválidos',
            '401': 'No autenticado'
        }
    }
}

TRAINING_DETAIL = {
    'get': {
        'description': 'Obtiene los detalles de un entrenamiento específico',
        'parameters': [
            {
                'name': 'pk',
                'required': True,
                'type': 'integer',
                'description': 'ID del entrenamiento'
            }
        ],
        'responses': {
            '200': 'Detalles del entrenamiento',
            '404': 'Entrenamiento no encontrado',
            '401': 'No autenticado'
        }
    },
    'put': {
        'description': 'Actualiza un entrenamiento existente',
        'parameters': [
            {
                'name': 'pk',
                'required': True,
                'type': 'integer',
                'description': 'ID del entrenamiento'
            },
            {
                'name': 'name',
                'required': False,
                'type': 'string',
                'description': 'Nombre del entrenamiento'
            },
            {
                'name': 'date',
                'required': False,
                'type': 'date',
                'description': 'Fecha del entrenamiento (YYYY-MM-DD)'
            },
            {
                'name': 'notes',
                'required': False,
                'type': 'string',
                'description': 'Notas adicionales'
            }
        ],
        'responses': {
            '200': 'Entrenamiento actualizado',
            '400': 'Datos inválidos',
            '404': 'Entrenamiento no encontrado',
            '401': 'No autenticado'
        }
    },
    'delete': {
        'description': 'Elimina un entrenamiento',
        'parameters': [
            {
                'name': 'pk',
                'required': True,
                'type': 'integer',
                'description': 'ID del entrenamiento'
            }
        ],
        'responses': {
            '204': 'Entrenamiento eliminado',
            '404': 'Entrenamiento no encontrado',
            '401': 'No autenticado'
        }
    }
}

# Sets API
SET_ENDPOINTS = {
    'save_set': {
        'post': {
            'description': 'Guarda un nuevo set en un entrenamiento',
            'parameters': [
                {
                    'name': 'training_id',
                    'required': True,
                    'type': 'integer',
                    'description': 'ID del entrenamiento'
                },
                {
                    'name': 'exercise_id',
                    'required': True,
                    'type': 'integer',
                    'description': 'ID del ejercicio'
                },
                {
                    'name': 'reps',
                    'required': True,
                    'type': 'integer',
                    'description': 'Número de repeticiones'
                },
                {
                    'name': 'weight',
                    'required': True,
                    'type': 'float',
                    'description': 'Peso utilizado'
                },
                {
                    'name': 'notes',
                    'required': False,
                    'type': 'string',
                    'description': 'Notas adicionales'
                }
            ],
            'responses': {
                '201': 'Set creado',
                '400': 'Datos inválidos',
                '401': 'No autenticado',
                '404': 'Entrenamiento o ejercicio no encontrado'
            }
        }
    }
} 