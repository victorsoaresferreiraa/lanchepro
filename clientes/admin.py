from django.contrib import admin
from .models import Cliente, ContaAberta

class ContaInline(admin.TabularInline):
    model = ContaAberta
    extra = 0
    readonly_fields = ['criado_em']

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'telefone', 'divida_total', 'ativo']
    search_fields = ['nome', 'telefone']
    inlines = [ContaInline]

@admin.register(ContaAberta)
class ContaAbertaAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'total', 'valor_pago', 'status', 'data_vencimento']
    list_filter = ['status', 'pago']
