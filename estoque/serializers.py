"""
SERIALIZERS = Converte objetos Python/Django para JSON (e vice-versa)
É o "tradutor" entre o banco de dados e a API REST
"""
from rest_framework import serializers
from .models import Produto, Categoria


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'


class ProdutoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    estoque_baixo = serializers.BooleanField(read_only=True)
    margem_lucro = serializers.FloatField(read_only=True)

    class Meta:
        model = Produto
        fields = [
            'id', 'nome', 'categoria', 'categoria_nome',
            'quantidade', 'preco', 'preco_custo', 'estoque_minimo',
            'descricao', 'ativo', 'estoque_baixo', 'margem_lucro',
            'criado_em', 'atualizado_em'
        ]
