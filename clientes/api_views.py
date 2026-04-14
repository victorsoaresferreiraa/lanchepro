from rest_framework import viewsets
from .models import Cliente
from .serializers import ClienteSerializer
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.filter(ativo=True)
    serializer_class = ClienteSerializer
