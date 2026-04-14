from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Produto, Categoria
from .forms import ProdutoForm


@login_required
def lista_produtos(request):
    produtos = Produto.objects.select_related('categoria').filter(ativo=True)
    busca = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')

    if busca:
        produtos = produtos.filter(Q(nome__icontains=busca) | Q(categoria__nome__icontains=busca))
    if categoria_id:
        produtos = produtos.filter(categoria_id=categoria_id)

    categorias = Categoria.objects.filter(ativo=True)
    todos_ativos = Produto.objects.filter(ativo=True)
    alertas = sum(1 for p in todos_ativos if p.estoque_baixo)

    return render(request, 'estoque/lista.html', {
        'produtos': produtos,
        'categorias': categorias,
        'busca': busca,
        'categoria_selecionada': categoria_id,
        'total_produtos': produtos.count(),
        'alertas_estoque': alertas,
    })


@login_required
def criar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save()
            messages.success(request, f'Produto "{produto.nome}" cadastrado com sucesso!')
            return redirect('estoque:lista')
    else:
        form = ProdutoForm()
    return render(request, 'estoque/form.html', {'form': form, 'titulo': 'Novo Produto'})


@login_required
def editar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Produto "{produto.nome}" atualizado!')
            return redirect('estoque:lista')
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'estoque/form.html', {'form': form, 'titulo': 'Editar Produto', 'produto': produto})


@login_required
def excluir_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        produto.ativo = False
        produto.save()
        messages.success(request, f'Produto "{produto.nome}" removido.')
        return redirect('estoque:lista')
    return render(request, 'estoque/confirmar_exclusao.html', {'produto': produto})


@login_required
def ajustar_estoque(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        quantidade = int(request.POST.get('quantidade', 0))
        tipo = request.POST.get('tipo', 'adicionar')
        if tipo == 'adicionar':
            produto.quantidade += quantidade
        else:
            if produto.quantidade >= quantidade:
                produto.quantidade -= quantidade
            else:
                messages.error(request, 'Quantidade insuficiente no estoque!')
                return redirect('estoque:lista')
        produto.save()
        messages.success(request, f'Estoque de "{produto.nome}" ajustado para {produto.quantidade} un.')
        return redirect('estoque:lista')
    return render(request, 'estoque/ajustar.html', {'produto': produto})
