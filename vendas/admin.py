from django.contrib import admin
from .models import Venda, ItemVenda

class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 0
    readonly_fields = ['total']

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente_nome', 'tipo_pagamento', 'total', 'status', 'criado_em']
    list_filter = ['tipo_pagamento', 'status', 'criado_em']
    search_fields = ['cliente_nome', 'numero']
    inlines = [ItemVendaInline]
    readonly_fields = ['criado_em']
