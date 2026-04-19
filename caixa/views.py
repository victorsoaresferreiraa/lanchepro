from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Caixa, MovimentacaoCaixa

@login_required
def lista_caixas(request):
    """
    A LISTA GERAL: Mostra o histórico dos últimos caixas abertos e fechados.
    """
    # Pega os últimos 30 caixas e já traz o nome do operador para ser rápido
    caixas = Caixa.objects.select_related('operador').all()[:30]
    
    # Verifica se existe algum caixa que ainda está aberto agora
    caixa_aberto = Caixa.objects.filter(status='ABERTO').first()
    
    return render(request, 'caixa/lista.html', {
        'caixas': caixas, 
        'caixa_aberto': caixa_aberto
    })


@login_required
def abrir_caixa(request):
    """
    O INÍCIO DO DIA: Coloca o dinheiro de troco na gaveta e começa o trabalho.
    """
    # REGRA: Não pode abrir dois caixas ao mesmo tempo!
    if Caixa.objects.filter(status='ABERTO').exists():
        messages.warning(request, 'Já existe um caixa aberto!')
        return redirect('caixa:lista')
    
    if request.method == 'POST':
        # Pega o valor que você começou (o "fundo de caixa")
        valor_inicial = float(request.POST.get('valor_inicial', 0))
        
        # Cria o registro do caixa
        caixa = Caixa.objects.create(
            operador=request.user,
            valor_inicial=valor_inicial,
        )
        
        # Registra o primeiro movimento: "Abertura"
        MovimentacaoCaixa.objects.create(
            caixa=caixa, 
            tipo='ABERTURA',
            valor=valor_inicial, 
            operador=request.user,
            descricao=f'Abertura de caixa com R$ {valor_inicial:.2f}'
        )
        
        messages.success(request, f'Caixa aberto com R$ {valor_inicial:.2f}')
        return redirect('caixa:lista')
    
    return render(request, 'caixa/abrir.html')


@login_required
def fechar_caixa(request):
    """
    O FIM DO EXPEDIENTE: Hora de contar o dinheiro e ver se sobrou ou faltou.
    """
    caixa = Caixa.objects.filter(status='ABERTO').first()
    if not caixa:
        messages.error(request, 'Nenhum caixa aberto!')
        return redirect('caixa:lista')
    
    if request.method == 'POST':
        # Quanto dinheiro tem na gaveta agora?
        valor_final = float(request.POST.get('valor_final', 0))
        
        caixa.valor_final = valor_final
        caixa.status = 'FECHADO'
        caixa.data_fechamento = timezone.now()
        caixa.observacoes = request.POST.get('observacoes', '')
        caixa.save()
        
        # Registra o movimento final: "Fechamento"
        MovimentacaoCaixa.objects.create(
            caixa=caixa, 
            tipo='FECHAMENTO',
            valor=valor_final, 
            operador=request.user,
            descricao='Fechamento de caixa'
        )
        
        messages.success(request, 'Caixa fechado com sucesso!')
        return redirect('caixa:lista')
    
    return render(request, 'caixa/fechar.html', {'caixa': caixa})


@login_required
def sangria(request):
    """
    A SANGRIA: Tirar dinheiro do caixa para pagar um fornecedor ou por segurança.
    """
    caixa = Caixa.objects.filter(status='ABERTO').first()
    if not caixa:
        messages.error(request, 'Nenhum caixa aberto!')
        return redirect('caixa:lista')
    
    if request.method == 'POST':
        valor = float(request.POST.get('valor', 0))
        motivo = request.POST.get('motivo', 'Sangria')
        
        # Atualiza o valor total que foi retirado do caixa
        caixa.valor_sangria += valor
        caixa.save()
        
        # Registra a movimentação para o patrão saber quem tirou o dinheiro
        MovimentacaoCaixa.objects.create(
            caixa=caixa, 
            tipo='SANGRIA', 
            valor=valor,
            descricao=motivo, 
            operador=request.user
        )
        
        messages.success(request, f'Sangria de R$ {valor:.2f} registrada.')
        return redirect('caixa:lista')
    
    return render(request, 'caixa/sangria.html', {'caixa': caixa})