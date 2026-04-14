from rest_framework import serializers
from .models import Venda, ItemVenda

class ItemVendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemVenda
        fields = ['id','produto','produto_nome','quantidade','preco_unitario','total']

class VendaSerializer(serializers.ModelSerializer):
    itens = ItemVendaSerializer(many=True, read_only=True)
    operador_nome = serializers.CharField(source='operador.username', read_only=True)
    class Meta:
        model = Venda
        fields = ['numero','cliente_nome','cliente_telefone','tipo_pagamento','status','subtotal','desconto','total','troco','operador_nome','criado_em','itens']
