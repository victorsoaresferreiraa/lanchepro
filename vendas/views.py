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
    """
    TELA DO BALCÃO: Mostra os produtos e o estado do caixa.
    """
    # Pega só o que tá ativo e tem no estoque para não vender o que não existe
    produtos = Produto.objects.filter(ativo=True, quantidade__gt=0).select_related('categoria')
    
    # Procura se tem algum caixa que foi aberto e ainda não fechou
    caixa_aberto = Caixa.objects.filter(status='ABERTO').first()
    
    return render(request, 'vendas/pdv.html', {
        'produtos': produtos,
        'caixa_aberto': caixa_aberto,
    })


@login_required
@transaction.atomic  # REGRA DE OURO: Se der erro no meio, ele desfaz tudo (protege seu estoque e dinheiro)
def finalizar_venda(request):
    """
    O MOTOR DA VENDA: Transforma o carrinho em dinheiro e baixa o estoque.
    """
    # Se o cara tentar entrar aqui sem ser enviando o formulário, manda ele de volta
    if request.method != 'POST':
        return redirect('vendas:pdv')
    
    # 1. SEGURANÇA: Não vende se a gaveta do dinheiro (caixa) estiver trancada
    caixa = Caixa.objects.filter(status='ABERTO').first()
    if not caixa:
        messages.error(request, 'Não há caixa aberto! Abra o caixa primeiro.')
        return redirect('caixa:lista')
    
    try:
        # Pega a lista de produtos que veio do navegador (em formato de texto/JSON)
        itens_json = request.POST.get('itens', '[]')
        itens = json.loads(itens_json) # Transforma o texto em uma lista que o Python entende
        
        if not itens:
            messages.error(request, 'Carrinho vazio!')
            return redirect('vendas:pdv')
        
        # 2. CRIA A VENDA: Começa a preencher o "papel" da venda no banco de dados
        venda = Venda.objects.create(
            cliente_nome=request.POST.get('cliente_nome', ''),
            cliente_telefone=request.POST.get('cliente_telefone', ''),
            tipo_pagamento=request.POST.get('tipo_pagamento', 'DINHEIRO'),
            desconto=request.POST.get('desconto', 0) or 0,
            operador=request.user, # Salva quem é o funcionário que está logado
        )
        
        subtotal = 0
        # 3. LOOP DOS ITENS: Vai pegando um por um do carrinho
        for item in itens:
            produto = get_object_or_404(Produto, id=item['produto_id'])
            qtd = int(item['quantidade'])
            
            # Checa se o espertinho não quer comprar mais do que tem na prateleira
            if not produto.pode_vender(qtd):
                raise ValueError(f'Estoque insuficiente para {produto.nome}')
            
            # Registra que esse produto específico faz parte dessa venda
            ItemVenda.objects.create(
                venda=venda,
                produto=produto,
                produto_nome=produto.nome,
                quantidade=qtd,
                preco_unitario=produto.preco,
            )
            
            # BAIXA DE ESTOQUE: Tira o produto da prateleira real
            produto.quantidade -= qtd
            produto.save()
            
            # Vai somando o valor de cada item para saber o total depois
            subtotal += produto.preco * qtd
        
        # 4. FECHAMENTO DA CONTA: Calcula totais, desconto e troco
        venda.subtotal = subtotal
        venda.total = subtotal - float(venda.desconto)
        troco_input = float(request.POST.get('troco', 0) or 0)
        venda.troco = troco_input
        venda.save() # Salva os valores finais na venda
        
        # 5. MOVIMENTAÇÃO DE CAIXA: Só coloca o dinheiro na gaveta se não for fiado
        if venda.tipo_pagamento != 'FIADO':
            caixa.valor_vendas += venda.total # Soma o dinheiro no saldo do caixa
            caixa.save()
            
            # Cria um registro histórico: "Entrou X reais da venda tal"
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
        # Se cair aqui, o @transaction.atomic cancela a venda e devolve os produtos pro estoque sozinho
        messages.error(request, str(e))
        return redirect('vendas:pdv')
    except Exception as e:
        # Se der qualquer outro erro doido, avisa o usuário
        messages.error(request, f'Erro ao processar venda: {e}')
        return redirect('vendas:pdv')


@login_required
def recibo(request, pk):
    """
    O COMPROVANTE: Busca a venda pelo número e mostra os itens dela.
    """
    venda = get_object_or_404(Venda.objects.prefetch_related('itens'), pk=pk)
    return render(request, 'vendas/recibo.html', {'venda': venda})


@login_required
def historico(request):
    """
    RELATÓRIO: Lista as vendas feitas para o patrão ver.
    """
    # Pega todas as vendas concluídas, já trazendo os nomes dos operadores para ser mais rápido
    vendas = Venda.objects.filter(status='CONCLUIDA').select_related('operador').prefetch_related('itens')
    
    # Se o usuário preencher as datas no filtro, a gente filtra a lista
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    if data_inicio:
        vendas = vendas.filter(criado_em__date__gte=data_inicio)
    if data_fim:
        vendas = vendas.filter(criado_em__date__lte=data_fim)
    
    # Faz a soma de tudo que foi vendido no período
    total_geral = vendas.aggregate(Sum('total'))['total__sum'] or 0
    
    return render(request, 'vendas/historico.html', {
        'vendas': vendas[:100], # Mostra só as últimas 100 para não travar o PC
        'total_geral': total_geral,
        'total_vendas': vendas.count(),
    })