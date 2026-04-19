from django.contrib import admin
from .models import Produto, Categoria

# --- CONFIGURAÇÃO DA TELA DE CATEGORIAS ---
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    # 1. O que aparece na tabela: Nome, se tá ativa e a data que foi criada
    list_display = ['nome', 'ativo', 'criado_em']
    
    # 2. Filtro lateral: Ajuda a achar rápido só as categorias ativas ou inativas
    list_filter = ['ativo']
    
    # 3. Barra de busca: Digita o nome e ele acha a categoria
    search_fields = ['nome']


# --- CONFIGURAÇÃO DA TELA DE PRODUTOS ---
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    # 1. COLUNAS: O que o gerente vê na lista principal. 
    # Note que o 'estoque_baixo' que a gente criou lá no Model aparece aqui como uma coluna!
    list_display = ['nome', 'categoria', 'quantidade', 'preco', 'estoque_baixo', 'ativo']
    
    # 2. FILTROS: Filtra por categoria (ex: só Bebidas) ou por status
    list_filter = ['categoria', 'ativo']
    
    # 3. BUSCA: Acha o produto pelo nome
    search_fields = ['nome']
    
    # 4. EDIÇÃO RÁPIDA: Isso aqui é foda! 
    # Permite mudar a quantidade e o preço direto na lista, sem precisar abrir o produto.
    # É como uma planilha de Excel onde você clica e digita.
    list_editable = ['quantidade', 'preco']
    
    # 5. SEGURANÇA: Campos que o gerente só pode ver, mas não pode mexer.
    # Datas de criação e atualização o banco de dados controla sozinho.
    readonly_fields = ['criado_em', 'atualizado_em']