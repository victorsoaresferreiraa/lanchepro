from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Produto, Categoria
from .serializers import ProdutoSerializer, CategoriaSerializer

# --- O MAESTRO DOS PRODUTOS ---
class ProdutoViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet = O "Tudo-em-Um". 
    Ele cria automaticamente os caminhos para:
    - Listar (GET)
    - Criar (POST)
    - Ver um só (GET com ID)
    - Editar (PUT/PATCH)
    - Excluir (DELETE)
    """
    # 1. FONTE DE DADOS: Pega só os produtos que não foram "deletados" (ativo=True)
    # O 'select_related' é aquele truque para carregar a categoria junto e ser mais rápido.
    queryset = Produto.objects.filter(ativo=True).select_related('categoria')
    serializer_class = ProdutoSerializer
    
    # 2. FERRAMENTAS DE BUSCA: Permite que o usuário filtre e ordene os produtos.
    # Se você mandar na URL: ?search=Coca, o Django já filtra sozinho!
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'categoria__nome'] # Onde a busca vai procurar
    ordering_fields = ['nome', 'preco', 'quantidade'] # O que pode ser ordenado

    # 3. O BOTÃO DE PÂNICO (Ação Customizada): 
    # Cria um endereço extra: /api/produtos/estoque_baixo/
    @action(detail=False, methods=['get'])
    def estoque_baixo(self, request):
        """Entrega uma lista só com os produtos que estão acabando."""
        # Filtra direto no banco quem está com a quantidade menor que o mínimo
        produtos = self.get_queryset().extra(where=['quantidade <= estoque_minimo'])
        serializer = self.get_serializer(produtos, many=True)
        return Response(serializer.data)


# --- O MAESTRO DAS CATEGORIAS ---
class CategoriaViewSet(viewsets.ModelViewSet):
    """Gerencia as pastas do estoque (Lanches, Bebidas, etc.) via API."""
    queryset = Categoria.objects.filter(ativo=True)
    serializer_class = CategoriaSerializer