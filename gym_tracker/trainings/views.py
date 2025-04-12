# Este archivo ahora importa las vistas desde las subcarpetas
from .views.api import TrainingDetailView
from .views.training_management import delete_training, toggle_complete, get_routine_days, create_training_from_routine
from .views.training_session import execute_training, training_session_view, save_set, save_set_simple, get_completed_sets
from .views.set_management import delete_set, edit_set
from .views.stats import training_stats, dashboard
from .views.profile import profile_edit
from .views.trainer import assigned_training_detail, create_training_session, edit_user_training

# Re-exportar las vistas para mantener la compatibilidad con las URLs
__all__ = [
    'TrainingDetailView',
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