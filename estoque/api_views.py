from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Produto, Categoria
from .serializers import ProdutoSerializer, CategoriaSerializer


class ProdutoViewSet(viewsets.ModelViewSet):
    """
    ViewSet = uma view que automaticamente tem:
    GET /produtos/         → lista todos
    POST /produtos/        → cria novo
    GET /produtos/1/       → detalhe do produto 1
    PUT /produtos/1/       → atualiza produto 1
    DELETE /produtos/1/    → apaga produto 1
    """
    queryset = Produto.objects.filter(ativo=True).select_related('categoria')
    serializer_class = ProdutoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'categoria__nome']
    ordering_fields = ['nome', 'preco', 'quantidade']

    @action(detail=False, methods=['get'])
    def estoque_baixo(self, request):
        """Endpoint customizado: GET /api/estoque/produtos/estoque_baixo/"""
        produtos = self.get_queryset().extra(where=['quantidade <= estoque_minimo'])
        serializer = self.get_serializer(produtos, many=True)
        return Response(serializer.data)


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.filter(ativo=True)
    serializer_class = CategoriaSerializer
