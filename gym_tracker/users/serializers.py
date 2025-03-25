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
        fields = ['id', 'username', 'email', 'role', 'is_superuser', 'peso', 'cuello', 'cintura', 'cadera', 'pecho', 'brazos', 'muslo', 'muñeca']
        extra_kwargs = {'password': {'write_only': True}}  # No incluir contraseña en las respuestas

class UserAdminSerializer(serializers.ModelSerializer):
    """
    Serializer para administración de usuarios.
    Incluye todos los campos necesarios para la gestión completa de usuarios.
    """
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'first_name', 'last_name', 
                  'is_active', 'is_superuser', 'date_joined', 'last_login', 'peso', 'cuello', 'cintura', 
                  'cadera', 'pecho', 'brazos', 'muslo', 'muñeca']
        read_only_fields = ['date_joined', 'last_login']
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        # Actualizar todos los campos excepto la contraseña
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Si se proporcionó una contraseña, actualizarla de forma segura
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance

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
        token['is_superuser'] = user.is_superuser
        return token
        
    def validate(self, attrs):
        data = super().validate(attrs)
        # Añadir información adicional a la respuesta
        data['username'] = self.user.username
        data['role'] = self.user.role
        data['email'] = self.user.email
        data['is_superuser'] = self.user.is_superuser
        return data
