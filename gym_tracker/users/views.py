from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, MyTokenObtainPairSerializer, UserSerializer, UserAdminSerializer
from .permissions import IsAdminUser
from django.contrib.auth import get_user_model, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from django.http import JsonResponse
import json

def csrf_token_view(request):
    """
    Vista simple para obtener un token CSRF.
    Esta vista se mantiene para compatibilidad.
    """
    return JsonResponse({'csrfToken': get_token(request)})

User = get_user_model()  # Obtener el modelo de usuario activo

class UserProfileView(generics.RetrieveAPIView):
    """
    Vista para obtener el perfil de un usuario.
    Esta vista es utilizada por la API.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Vistas de administración de usuarios
class UserListView(generics.ListCreateAPIView):
    """
    Vista para listar todos los usuarios y crear nuevos.
    Solo accesible para administradores.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserAdminSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar o eliminar un usuario específico.
    Solo accesible para administradores.
    """
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

# Las siguientes vistas están marcadas como obsoletas pero se mantienen para compatibilidad API
# Deberían usarse las vistas estándar de Django para autenticación en su lugar

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    """
    Vista para registrar un nuevo usuario.
    NOTA: Esta vista está obsoleta. Use las vistas estándar de Django en su lugar.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        print("ADVERTENCIA: Usando vista de registro obsoleta")
        try:
            if isinstance(request.data, dict) and request.data:
                data = request.data
            else:
                data = json.loads(request.body.decode('utf-8'))
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            data = request.data
        
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Redirigir a la página de inicio de sesión
            return Response({
                'success': True,
                'message': 'Usuario registrado correctamente. Por favor inicie sesión.',
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class MyTokenObtainPairView(TokenObtainPairView):
    """
    Vista personalizada para obtener tokens JWT.
    NOTA: Esta vista está obsoleta. Use las vistas estándar de Django en su lugar.
    """
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [AllowAny]