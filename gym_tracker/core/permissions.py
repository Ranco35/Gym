from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo a los propietarios de un objeto editarlo.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsTrainerOrAdmin(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo a entrenadores o administradores.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'TRAINER' or 
            request.user.is_staff or 
            request.user.is_superuser
        )

class IsTrainerForUser(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo al entrenador asignado al usuario.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated and
            hasattr(obj, 'user') and
            request.user.trainer_set.filter(students=obj.user).exists()
        ) 