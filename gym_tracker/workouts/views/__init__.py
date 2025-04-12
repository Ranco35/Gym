# Este archivo permite que la carpeta views sea un paquete de Python 

# Importar vistas desde api.py
from .api import WorkoutListCreateView, WorkoutDetailView

# Importar vistas desde routines.py
from .routines import routine_selection, routine_list, routine_detail

# Importar vistas desde routine_days.py
from .routine_days import routine_day_detail, delete_routine_exercise, update_routine_focus

# Importar vistas desde routine_management.py
from .routine_management import edit_routine, delete_routine, view_assigned_routine

# Re-exportar las vistas para mantener la compatibilidad
__all__ = [
    'WorkoutListCreateView',
    'WorkoutDetailView',
    'routine_selection',
    'routine_list',
    'routine_detail',
    'routine_day_detail',
    'delete_routine_exercise',
    'update_routine_focus',
    'edit_routine',
    'delete_routine',
    'view_assigned_routine',
] 