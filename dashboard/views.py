from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from datetime import timedelta
from vendas.models import Venda, ItemVenda
from estoque.models import Produto
from clientes.models import ContaAberta
from caixa.models import Caixa


@login_required
def dashboard(request):
    hoje = timezone.now().date()
    inicio_mes = hoje.replace(day=1)
    
    # --- MÉTRICAS DO DIA ---
    vendas_hoje = Venda.objects.filter(
        criado_em__date=hoje, status='CONCLUIDA'
    ).aggregate(total=Sum('total'), count=Count('numero'))
    
    # --- MÉTRICAS DO MÊS ---
    vendas_mes = Venda.objects.filter(
        criado_em__date__gte=inicio_mes, status='CONCLUIDA'
    ).aggregate(total=Sum('total'), count=Count('numero'))
    
    # --- TICKET MÉDIO ---
    ticket_medio = (vendas_mes['total'] or 0) / max(vendas_mes['count'] or 1, 1)
    
    # --- PRODUTOS MAIS VENDIDOS (TOP 5) ---
    top_produtos = ItemVenda.objects.filter(
        venda__criado_em__date__gte=inicio_mes
    ).values('produto_nome').annotate(
        total_qtd=Sum('quantidade'),
        total_valor=Sum('total')
    ).order_by('-total_qtd')[:5]
    
    # --- ESTOQUE BAIXO ---
    produtos_alerta = Produto.objects.filter(ativo=True).extra(
        where=['quantidade <= estoque_minimo']
    )
    
    # --- CONTAS EM ABERTO ---
    contas_abertas = ContaAberta.objects.filter(pago=False)
    total_fiado = contas_abertas.aggregate(t=Sum('total'))['t'] or 0
    
    # --- CAIXA ATUAL ---
    caixa_aberto = Caixa.objects.filter(status='ABERTO').first()
    
    # --- VENDAS ÚLTIMOS 7 DIAS (para gráfico) ---
    vendas_7dias = []
    for i in range(6, -1, -1):
        dia = hoje - timedelta(days=i)
        total = Venda.objects.filter(
            criado_em__date=dia, status='CONCLUIDA'
        ).aggregate(t=Sum('total'))['t'] or 0
        vendas_7dias.append({
            'dia': dia.strftime('%d/%m'),
            'total': float(total)
        })
    
    return render(request, 'dashboard/index.html', {
        'vendas_hoje': vendas_hoje,
        'vendas_mes': vendas_mes,
        'ticket_medio': ticket_medio,
        'top_produtos': top_produtos,
        'produtos_alerta': produtos_alerta,
        'total_fiado': total_fiado,
        'contas_abertas_count': contas_abertas.count(),
        'caixa_aberto': caixa_aberto,
        'vendas_7dias': vendas_7dias,
        'total_produtos': Produto.objects.filter(ativo=True).count(),
    })
