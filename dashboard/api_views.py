from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Count
from vendas.models import Venda
from estoque.models import Produto
from clientes.models import ContaAberta


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def metricas(request):
    """
    Endpoint: GET /api/dashboard/metricas/
    Retorna JSON com métricas para o dashboard
    Útil para apps mobile ou atualização sem recarregar página (AJAX)
    """
    hoje = timezone.now().date()
    vendas_hoje = Venda.objects.filter(
        criado_em__date=hoje, status='CONCLUIDA'
    ).aggregate(total=Sum('total'), count=Count('numero'))
    
    return Response({
        'vendas_hoje': {
            'total': float(vendas_hoje['total'] or 0),
            'quantidade': vendas_hoje['count'] or 0,
        },
        'estoque_baixo': Produto.objects.filter(ativo=True).extra(
            where=['quantidade <= estoque_minimo']
        ).count(),
        'fiado_aberto': float(
            ContaAberta.objects.filter(pago=False).aggregate(
                t=Sum('total'))['t'] or 0
        ),
    })
