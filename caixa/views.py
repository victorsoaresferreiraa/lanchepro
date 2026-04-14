from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Caixa, MovimentacaoCaixa


@login_required
def lista_caixas(request):
    caixas = Caixa.objects.select_related('operador').all()[:30]
    caixa_aberto = Caixa.objects.filter(status='ABERTO').first()
    return render(request, 'caixa/lista.html', {'caixas': caixas, 'caixa_aberto': caixa_aberto})


@login_required
def abrir_caixa(request):
    if Caixa.objects.filter(status='ABERTO').exists():
        messages.warning(request, 'Já existe um caixa aberto!')
        return redirect('caixa:lista')
    
    if request.method == 'POST':
        valor_inicial = float(request.POST.get('valor_inicial', 0))
        caixa = Caixa.objects.create(
            operador=request.user,
            valor_inicial=valor_inicial,
        )
        MovimentacaoCaixa.objects.create(
            caixa=caixa, tipo='ABERTURA',
            valor=valor_inicial, operador=request.user,
            descricao=f'Abertura de caixa com R$ {valor_inicial:.2f}'
        )
        messages.success(request, f'Caixa aberto com R$ {valor_inicial:.2f}')
        return redirect('caixa:lista')
    
    return render(request, 'caixa/abrir.html')


@login_required
def fechar_caixa(request):
    caixa = Caixa.objects.filter(status='ABERTO').first()
    if not caixa:
        messages.error(request, 'Nenhum caixa aberto!')
        return redirect('caixa:lista')
    
    if request.method == 'POST':
        valor_final = float(request.POST.get('valor_final', 0))
        caixa.valor_final = valor_final
        caixa.status = 'FECHADO'
        caixa.data_fechamento = timezone.now()
        caixa.observacoes = request.POST.get('observacoes', '')
        caixa.save()
        MovimentacaoCaixa.objects.create(
            caixa=caixa, tipo='FECHAMENTO',
            valor=valor_final, operador=request.user,
            descricao='Fechamento de caixa'
        )
        messages.success(request, 'Caixa fechado com sucesso!')
        return redirect('caixa:lista')
    
    return render(request, 'caixa/fechar.html', {'caixa': caixa})


@login_required
def sangria(request):
    caixa = Caixa.objects.filter(status='ABERTO').first()
    if not caixa:
        messages.error(request, 'Nenhum caixa aberto!')
        return redirect('caixa:lista')
    
    if request.method == 'POST':
        valor = float(request.POST.get('valor', 0))
        motivo = request.POST.get('motivo', 'Sangria')
        caixa.valor_sangria += valor
        caixa.save()
        MovimentacaoCaixa.objects.create(
            caixa=caixa, tipo='SANGRIA', valor=valor,
            descricao=motivo, operador=request.user
        )
        messages.success(request, f'Sangria de R$ {valor:.2f} registrada.')
        return redirect('caixa:lista')
    
    return render(request, 'caixa/sangria.html', {'caixa': caixa})
