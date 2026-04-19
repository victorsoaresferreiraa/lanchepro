from rest_framework import viewsets
from .models import Venda
from .serializers import VendaSerializer

# O 'ReadOnlyModelViewSet' é um garçom que SÓ ENTREGA pedidos.
# Ele não deixa ninguém de fora cadastrar, mudar ou apagar vendas por aqui.
# É usado para segurança: para criar vendas, usamos aquela função 'finalizar_venda' que a gente viu antes.
class VendaViewSet(viewsets.ReadOnlyModelViewSet):
    
    # 1. O ESTOQUE DO GARÇOM: Aqui dizemos quais vendas ele pode entregar.
    # O 'prefetch_related' é como se o garçom já trouxesse os talheres junto com o prato
    # (ele já carrega os itens da venda de uma vez para o sistema não ficar lento).
    queryset = Venda.objects.all().prefetch_related('itens')
    
    # 2. O TRADUTOR: Aqui dizemos qual "tradutor" (Serializer) o garçom deve usar
    # para transformar a venda em um texto (JSON) que o celular entenda.
    serializer_class = VendaSerializer