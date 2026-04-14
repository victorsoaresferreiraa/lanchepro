from rest_framework import serializers
from .models import Caixa, MovimentacaoCaixa
class MovimentacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimentacaoCaixa
        fields = '__all__'
class CaixaSerializer(serializers.ModelSerializer):
    movimentacoes = MovimentacaoSerializer(many=True, read_only=True)
    saldo_esperado = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = Caixa
        fields = '__all__'
