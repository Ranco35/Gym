from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def trainer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Temporalmente permitir acceso sin verificación
        return view_func(request, *args, **kwargs)
    return _wrapped_view 