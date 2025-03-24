from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()  # Obtener el modelo de usuario personalizado

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo User.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'peso', 'cuello', 'cintura', 'cadera', 'pecho', 'brazos', 'muslo', 'muñeca']
        extra_kwargs = {'password': {'write_only': True}}  # No incluir contraseña en las respuestas

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para registrar un nuevo usuario.
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'role']
        extra_kwargs = {
            'role': {'required': False},
        }

    def validate(self, attrs):
        if 'password2' in attrs and attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)  # Eliminar password2 si existe
        role = validated_data.pop('role', 'USER')  # Obtener rol o usar USER como predeterminado
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=role
        )
        return user

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para obtener tokens JWT.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Agregar datos personalizados al token
        token['username'] = user.username
        token['role'] = user.role
        token['email'] = user.email
        return token
        
    def validate(self, attrs):
        data = super().validate(attrs)
        # Añadir información adicional a la respuesta
        data['username'] = self.user.username
        data['role'] = self.user.role
        data['email'] = self.user.email
        return data
