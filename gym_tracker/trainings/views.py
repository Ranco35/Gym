from rest_framework import generics, permissions
from .models import Training
from .serializers import TrainingSerializer

class TrainingListCreateView(generics.ListCreateAPIView):
    """
    Vista para listar y crear entrenamientos.
    """
    serializer_class = TrainingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Obtiene los entrenamientos del usuario autenticado.
        """
        return Training.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Asigna el usuario autenticado al crear un nuevo entrenamiento.
        """
        serializer.save(user=self.request.user)

class TrainingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar o eliminar un entrenamiento.
    """
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer
    permission_classes = [permissions.IsAuthenticated]