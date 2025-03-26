from django.http import HttpResponse
from django.middleware.csrf import get_token

# Simplificado para compatibilidad con versiones anteriores
class OptionsMiddleware:
    """
    Middleware para manejar solicitudes OPTIONS y asegurar que el token CSRF esté disponible.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Para peticiones OPTIONS que podrían ser de CORS preflight
        if request.method == "OPTIONS":
            response = HttpResponse()
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type, X-CSRFToken"
            return response
        
        # Asegurarse de que el token CSRF esté en la sesión para GET
        if request.method == "GET":
            get_token(request)
            
        # Procesar la solicitud normalmente
        return self.get_response(request) 