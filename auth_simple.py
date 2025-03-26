from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@csrf_exempt
def simple_auth(request):
    """
    Vista extremadamente simple para autenticación
    """
    logger.debug(f"Método recibido: {request.method}")
    logger.debug(f"Ruta: {request.path}")
    
    # Para OPTIONS responder correctamente para CORS
    if request.method == 'OPTIONS':
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response['Access-Control-Max-Age'] = '86400'  # 24 horas
        return response
    
    # Para POST procesar la autenticación
    if request.method == 'POST':
        try:
            # Decodificar el cuerpo de la solicitud
            body = request.body.decode('utf-8')
            logger.debug(f"Body recibido: {body}")
            
            # Intentar decodificar como JSON
            data = json.loads(body)
            username = data.get('username')
            password = data.get('password')
            
            logger.debug(f"Usuario: {username}, Password: {'*' * len(password) if password else 'No proporcionado'}")
            
            # Autenticar usuario
            user = authenticate(username=username, password=password)
            
            if user:
                # Generar token JWT
                refresh = RefreshToken.for_user(user)
                
                # Crear respuesta con CORS habilitado
                response = JsonResponse({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'username': user.username,
                    'email': user.email
                })
                
                # Agregar cabeceras CORS
                response['Access-Control-Allow-Origin'] = '*'
                return response
            else:
                # Autenticación fallida
                response = JsonResponse({
                    'error': 'Credenciales inválidas'
                }, status=401)
                
                # Agregar cabeceras CORS
                response['Access-Control-Allow-Origin'] = '*'
                return response
                
        except Exception as e:
            # Error al procesar la solicitud
            logger.exception(f"Error: {str(e)}")
            
            response = JsonResponse({
                'error': str(e)
            }, status=400)
            
            # Agregar cabeceras CORS
            response['Access-Control-Allow-Origin'] = '*'
            return response
    
    # Método no permitido
    response = JsonResponse({
        'error': 'Método no permitido'
    }, status=405)
    
    # Agregar cabeceras CORS
    response['Access-Control-Allow-Origin'] = '*'
    return response 