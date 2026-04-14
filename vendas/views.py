from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, Count
from .models import Venda, ItemVenda
from estoque.models import Produto
from caixa.models import Caixa, MovimentacaoCaixa
import json


@login_required
def pdv(request):
    """PDV = Ponto de Venda. A tela principal de vendas."""
    produtos = Produto.objects.filter(ativo=True, quantidade__gt=0).select_related('categoria')
    caixa_aberto = Caixa.objects.filter(status='ABERTO').first()
    
    return render(request, 'vendas/pdv.html', {
        'produtos': produtos,
        'caixa_aberto': caixa_aberto,
    })


@login_required
@transaction.atomic  # Se algo falhar, cancela TUDO (consistência!)
def finalizar_venda(request):
    """
    Processa a venda: 
    1. Cria registro da venda
    2. Cria itens da venda
    3. Baixa do estoque
    4. Registra no caixa
    """
    if request.method != 'POST':
        return redirect('vendas:pdv')
    
    # Verifica se tem caixa aberto
    caixa = Caixa.objects.filter(status='ABERTO').first()
    if not caixa:
        messages.error(request, 'Não há caixa aberto! Abra o caixa primeiro.')
        return redirect('caixa:lista')
    
    try:
        itens_json = request.POST.get('itens', '[]')
        itens = json.loads(itens_json)
        
        if not itens:
            messages.error(request, 'Carrinho vazio!')
            return redirect('vendas:pdv')
        
        # Cria a venda
        venda = Venda.objects.create(
            cliente_nome=request.POST.get('cliente_nome', ''),
            cliente_telefone=request.POST.get('cliente_telefone', ''),
            tipo_pagamento=request.POST.get('tipo_pagamento', 'DINHEIRO'),
            desconto=request.POST.get('desconto', 0) or 0,
            operador=request.user,
        )
        
        subtotal = 0
        # Cria cada item e baixa do estoque
        for item in itens:
            produto = get_object_or_404(Produto, id=item['produto_id'])
            qtd = int(item['quantidade'])
            
            if not produto.pode_vender(qtd):
                raise ValueError(f'Estoque insuficiente para {produto.nome}')
            
            ItemVenda.objects.create(
                venda=venda,
                produto=produto,
                produto_nome=produto.nome,
                quantidade=qtd,
                preco_unitario=produto.preco,
            )
            
            # Baixa do estoque
            produto.quantidade -= qtd
            produto.save()
            
            subtotal += produto.preco * qtd
        
        # Atualiza totais da venda
        venda.subtotal = subtotal
        venda.total = subtotal - float(venda.desconto)
        troco_input = float(request.POST.get('troco', 0) or 0)
        venda.troco = troco_input
        venda.save()
        
        # Registra no caixa (só se não for fiado)
        if venda.tipo_pagamento != 'FIADO':
            caixa.valor_vendas += venda.total
            caixa.save()
            
            MovimentacaoCaixa.objects.create(
                caixa=caixa,
                tipo='VENDA',
                valor=venda.total,
                descricao=f'Venda #{venda.numero} - {venda.tipo_pagamento}',
                operador=request.user,
            )
        
        messages.success(request, f'Venda #{venda.numero} realizada! Total: R$ {venda.total:.2f}')
        return redirect('vendas:recibo', pk=venda.numero)
    
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('vendas:pdv')
    except Exception as e:
        messages.error(request, f'Erro ao processar venda: {e}')
        return redirect('vendas:pdv')


@login_required
def recibo(request, pk):
    venda = get_object_or_404(Venda.objects.prefetch_related('itens'), pk=pk)
    return render(request, 'vendas/recibo.html', {'venda': venda})


@login_required
def historico(request):
    vendas = Venda.objects.filter(status='CONCLUIDA').select_related('operador').prefetch_related('itens')
    
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    if data_inicio:
        vendas = vendas.filter(criado_em__date__gte=data_inicio)
    if data_fim:
        vendas = vendas.filter(criado_em__date__lte=data_fim)
    
    total_geral = vendas.aggregate(Sum('total'))['total__sum'] or 0
    
    return render(request, 'vendas/historico.html', {
        'vendas': vendas[:100],
        'total_geral': total_geral,
        'total_vendas': vendas.count(),
    })
