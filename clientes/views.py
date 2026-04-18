from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from .models import Cliente, ContaAberta


@login_required
def lista_clientes(request):
    clientes = Cliente.objects.filter(ativo=True).annotate(
        total_devido=Sum('contas__total', filter=models_Q(contas__pago=False))
    )
    return render(request, 'clientes/lista.html', {'clientes': clientes})


def models_Q(**kwargs):
    from django.db.models import Q
    return Q(**kwargs)


@login_required
def detalhe_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    contas = cliente.contas.all()
    return render(request, 'clientes/detalhe.html', {
        'cliente': cliente,
        'contas': contas,
        'divida_total': cliente.divida_total,
    })


@login_required
def criar_conta_aberta(request):
    clientes = Cliente.objects.filter(ativo=True)
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        cliente = get_object_or_404(Cliente, pk=cliente_id)
        ContaAberta.objects.create(
            cliente=cliente,
            descricao=request.POST.get('descricao'),
            total=request.POST.get('total'),
            data_vencimento=request.POST.get('data_vencimento') or None,
            observacoes=request.POST.get('observacoes', ''),
        )
        messages.success(request, f'Conta em aberto registrada para {cliente.nome}')
        return redirect('clientes:detalhe', pk=cliente_id)
    return render(request, 'clientes/nova_conta.html', {'clientes': clientes})


@login_required
def registrar_pagamento(request, pk):
    conta = get_object_or_404(ContaAberta, pk=pk)
    if request.method == 'POST':
        valor = float(request.POST.get('valor', conta.total))
        from decimal import Decimal; conta.valor_pago += Decimal(str(valor))
        if conta.valor_pago >= float(conta.total):
            conta.pago = True
            conta.status = 'PAGO'
            conta.data_pagamento = timezone.now()
        else:
            conta.status = 'PARCIAL'
        conta.save()
        messages.success(request, f'Pagamento de R$ {valor:.2f} registrado!')
        return redirect('clientes:detalhe', pk=conta.cliente.pk)
    return render(request, 'clientes/pagamento.html', {'conta': conta})
