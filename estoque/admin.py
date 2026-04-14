from django.contrib import admin
from .models import Produto, Categoria

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo', 'criado_em']
    list_filter = ['ativo']
    search_fields = ['nome']

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'quantidade', 'preco', 'estoque_baixo', 'ativo']
    list_filter = ['categoria', 'ativo']
    search_fields = ['nome']
    list_editable = ['quantidade', 'preco']
    readonly_fields = ['criado_em', 'atualizado_em']
