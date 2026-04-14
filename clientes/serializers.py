from rest_framework import serializers
from .models import Cliente, ContaAberta
class ContaAbertaSerializer(serializers.ModelSerializer):
    saldo_devedor = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = ContaAberta
        fields = '__all__'
class ClienteSerializer(serializers.ModelSerializer):
    divida_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    contas = ContaAbertaSerializer(many=True, read_only=True)
    class Meta:
        model = Cliente
        fields = '__all__'
