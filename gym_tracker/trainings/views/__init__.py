# Este archivo permite que la carpeta views sea un paquete de Python 

# Importar vistas desde api.py
from .api import (
    TrainingDetailView,
    TrainingListView,
    RoutineDatesView,
    RoutineDateExercisesView
)

# Importar vistas desde training_management.py
from .training_management import delete_training, toggle_complete, get_routine_days, create_training_from_routine

# Importar vistas desde training_session.py
from .training_session import execute_training, training_session_view, save_set, save_set_simple, get_completed_sets

# Importar vistas desde set_management.py
from .set_management import delete_set, edit_set

# Importar vistas desde stats.py
from .stats import training_stats, dashboard

# Importar vistas desde profile.py
from .profile import profile_edit

# Importar vistas desde trainer.py
from .trainer import assigned_training_detail, create_training_session, edit_user_training

# Re-exportar las vistas para mantener la compatibilidad
__all__ = [
    'TrainingDetailView',
    'TrainingListView',
    'RoutineDatesView',
    'RoutineDateExercisesView',
    'delete_training',
    'toggle_complete',
    'get_routine_days',
    'create_training_from_routine',
    'execute_training',
    'training_session_view',
    'save_set',
    'save_set_simple',
    'get_completed_sets',
    'delete_set',
    'edit_set',
    'training_stats',
    'dashboard',
    'profile_edit',
    'assigned_training_detail',
    'create_training_session',
    'edit_user_training'
] 