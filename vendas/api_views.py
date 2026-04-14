from rest_framework import viewsets
from .models import Venda
from .serializers import VendaSerializer
class VendaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Venda.objects.all().prefetch_related('itens')
    serializer_class = VendaSerializer
