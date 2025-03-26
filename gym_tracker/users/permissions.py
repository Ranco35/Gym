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
        getattr(user, 'role', None) == 'ADMIN' or user.is_superuser
    ) 