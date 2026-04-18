from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count
from django.db.models.functions import ExtractHour
from datetime import date, datetime, timedelta
from vendas.models import Venda, ItemVenda
from estoque.models import Produto
from clientes.models import ContaAberta
from caixa.models import Caixa
from .services import gerar_relatorio_excel, gerar_relatorio_caixa_excel


@login_required
def painel_relatorios(request):
    hoje = date.today()
    inicio_mes = hoje.replace(day=1)
    vendas_mes = Venda.objects.filter(
        criado_em__date__gte=inicio_mes, status='CONCLUIDA'
    ).aggregate(total=Sum('total'), qtd=Count('numero'))
    top5 = ItemVenda.objects.filter(
        venda__criado_em__date__gte=inicio_mes, venda__status='CONCLUIDA',
    ).values('produto_nome').annotate(
        qtd=Sum('quantidade'), receita=Sum('total')
    ).order_by('-receita')[:5]
    return render(request, 'relatorios/painel.html', {
        'hoje': hoje, 'inicio_mes': inicio_mes,
        'vendas_mes': vendas_mes, 'top5': top5,
        'total_fiado': ContaAberta.objects.filter(pago=False).aggregate(t=Sum('total'))['t'] or 0,
        'caixas_recentes': Caixa.objects.select_related('operador').all()[:5],
        'total_produtos': Produto.objects.filter(ativo=True).count(),
        'prod_baixo': sum(1 for p in Produto.objects.filter(ativo=True) if p.estoque_baixo),
    })


@login_required
def download_relatorio_excel(request):
    hoje = date.today()
    try:
        di = datetime.strptime(request.GET.get('inicio',''), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        di = hoje.replace(day=1)
    try:
        df = datetime.strptime(request.GET.get('fim',''), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        df = hoje

    buffer = gerar_relatorio_excel(di, df)
    nome = f"lanchopro_{di.strftime('%Y%m%d')}_{df.strftime('%Y%m%d')}.xlsx"
    response = HttpResponse(
        buffer.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="{nome}"'
    return response


@login_required
def download_relatorio_caixa(request, caixa_id):
    caixa = get_object_or_404(Caixa, pk=caixa_id)
    buffer = gerar_relatorio_caixa_excel(caixa)
    nome = f"caixa_{caixa.data_abertura.strftime('%Y%m%d')}.xlsx"
    response = HttpResponse(buffer.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{nome}"'
    return response


@login_required
def api_dados_grafico(request):
    tipo = request.GET.get('tipo', 'vendas_7dias')
    hoje = date.today()
    if tipo == 'vendas_7dias':
        dados = []
        for i in range(6, -1, -1):
            dia = hoje - timedelta(days=i)
            total = Venda.objects.filter(
                criado_em__date=dia, status='CONCLUIDA'
            ).aggregate(t=Sum('total'))['t'] or 0
            dados.append({'dia': dia.strftime('%d/%m'), 'total': float(total)})
        return JsonResponse({'dados': dados})
    elif tipo == 'heatmap_horas':
        horas = Venda.objects.filter(
            criado_em__date__gte=hoje.replace(day=1), status='CONCLUIDA',
        ).annotate(hora=ExtractHour('criado_em')).values('hora').annotate(
            qtd=Count('numero'), total=Sum('total')
        ).order_by('hora')
        dados = {str(h['hora']): {'qtd': h['qtd'], 'total': float(h['total'])} for h in horas}
        return JsonResponse({'dados': dados})
    return JsonResponse({'erro': 'Tipo invalido'}, status=400)
