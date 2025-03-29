from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Permiso personalizado para permitir a usuarios con rol ADMIN o superusuarios.
    """
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.role == 'ADMIN' or request.user.is_superuser)
        )

def is_admin_or_superuser(user):
    """
    Función auxiliar para comprobar si un usuario es administrador o superusuario.
    Utilizada con el decorador user_passes_test.
    """
    return user.is_authenticated and (
        getattr(user, 'role', None) == 'ADMIN' or 
        getattr(user, 'role', None) == 'TRAINER' or 
        user.is_superuser
    )

def is_trainer_or_admin(user):
    """
    Función auxiliar para comprobar si un usuario es entrenador, administrador o superusuario.
    Utilizada con el decorador user_passes_test.
    """
    return user.is_authenticated and (
        getattr(user, 'role', None) == 'TRAINER' or
        getattr(user, 'role', None) == 'ADMIN' or
        user.is_superuser
    )
    
def can_edit_exercise(user, exercise):
    """
    Función auxiliar para comprobar si un usuario puede editar un ejercicio específico.
    Los superusuarios y administradores pueden editar cualquier ejercicio.
    Los entrenadores solo pueden editar los ejercicios que ellos crearon.
    """
    # Superusuarios y administradores pueden editar cualquier ejercicio
    if user.is_superuser or getattr(user, 'role', None) == 'ADMIN':
        return True
    
    # Entrenadores pueden editar cualquier ejercicio
    if getattr(user, 'role', None) == 'TRAINER':
        return True
    
    # Otros usuarios no pueden editar ejercicios
    return False 