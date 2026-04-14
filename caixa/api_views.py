from rest_framework import viewsets
from .models import Caixa
from .serializers import CaixaSerializer
class CaixaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Caixa.objects.all()
    serializer_class = CaixaSerializer
