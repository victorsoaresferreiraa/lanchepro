from rest_framework import serializers
from .models import Venda, ItemVenda

# --- TRADUTOR DOS ITENS (A lista de compras) ---
class ItemVendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemVenda
        # Aqui você diz quais "colunas" do banco você quer transformar em texto
        # O 'total' aqui é um campo calculado que o tradutor já entrega pronto
        fields = ['id', 'produto', 'produto_nome', 'quantidade', 'preco_unitario', 'total']

# --- TRADUTOR DA VENDA COMPLETA (O cabeçalho do pedido) ---
class VendaSerializer(serializers.ModelSerializer):
    # 1. TRADUÇÃO ANINHADA: Como uma venda tem vários itens, a gente chama o tradutor 
    # de itens lá de cima para listar tudo aqui dentro. 'many=True' = "tem vários".
    itens = ItemVendaSerializer(many=True, read_only=True)
    
    # 2. BUSCA PERSONALIZADA: Em vez de mostrar o ID do operador (ex: "Operador 1"), 
    # ele vai lá na tabela de usuários e busca o 'username' (ex: "Victor").
    operador_nome = serializers.CharField(source='operador.username', read_only=True)

    class Meta:
        model = Venda
        # Lista de tudo que vai aparecer no "relatório" final em JSON
        fields = [
            'numero', 'cliente_nome', 'cliente_telefone', 
            'tipo_pagamento', 'status', 'subtotal', 
            'desconto', 'total', 'troco', 'operador_nome', 
            'criado_em', 'itens'
        ]