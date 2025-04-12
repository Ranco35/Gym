from django.contrib.auth.decorators import login_required, user_passes_test

# Importar vistas desde las subcarpetas
from .views.api import WorkoutListCreateView, WorkoutDetailView
from .views.routines import routine_selection, routine_list, routine_detail
from .views.routine_days import routine_day_detail, delete_routine_exercise, update_routine_focus
from .views.routine_management import edit_routine, delete_routine, view_assigned_routine

# Función de verificación para comprobar si un usuario es administrador o superusuario
def is_admin_or_superuser(user):
    return user.is_authenticated and (user.role == 'ADMIN' or user.is_superuser)

# Re-exportar las vistas para mantener la compatibilidad con las URLs
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
    'is_admin_or_superuser'
]