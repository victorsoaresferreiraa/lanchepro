from django.contrib import admin
from .models import Venda, ItemVenda

# --- OS ITENS DENTRO DA VENDA (Visão em Linhas) ---
class ItemVendaInline(admin.TabularInline):
    """
    Isso aqui é um "truque" para você conseguir ver os produtos 
    diretamente dentro da página da Venda, sem ter que abrir outra tela.
    """
    model = ItemVenda
    extra = 0  # Não fica aparecendo aquelas linhas vazias chatas no final
    readonly_fields = ['total']  # O chefe não pode mudar o total na mão, o sistema calcula sozinho

# --- A TELA DE GERENCIAMENTO DE VENDAS ---
@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    # 1. O que aparece na tabela principal (a lista de vendas)
    list_display = ['numero', 'cliente_nome', 'tipo_pagamento', 'total', 'status', 'criado_em']
    
    # 2. Filtros na lateral direita (facilita achar vendas por tipo ou status)
    list_filter = ['tipo_pagamento', 'status', 'criado_em']
    
    # 3. Barra de busca: você pode digitar o nome do cliente ou o número da venda
    search_fields = ['cliente_nome', 'numero']
    
    # 4. Coloca os itens (produtos) para aparecerem "embutidos" na venda
    inlines = [ItemVendaInline]
    
    # 5. Segurança: a data de criação não pode ser editada, é só pra ver
    readonly_fields = ['criado_em']