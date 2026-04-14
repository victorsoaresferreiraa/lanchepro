from django.contrib import admin
from .models import Caixa, MovimentacaoCaixa

class MovInline(admin.TabularInline):
    model = MovimentacaoCaixa
    extra = 0
    readonly_fields = ['data_hora']

@admin.register(Caixa)
class CaixaAdmin(admin.ModelAdmin):
    list_display = ['id', 'operador', 'data_abertura', 'valor_vendas', 'status']
    list_filter = ['status']
    inlines = [MovInline]
