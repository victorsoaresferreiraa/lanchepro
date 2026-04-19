"""
SERIALIZERS = Converte objetos Python/Django para JSON (e vice-versa)
É o "tradutor" entre o banco de dados e a API REST
"""
from rest_framework import serializers
from .models import Produto, Categoria

# --- TRADUTOR DE CATEGORIAS (Ex: Lanches, Bebidas, Sobremesas) ---
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        # '__all__' é o jeito preguiçoso (e eficiente) de dizer: 
        # "Pegue todas as colunas que existem na tabela de categorias".
        fields = '__all__'


# --- TRADUTOR DE PRODUTOS (O prato principal) ---
class ProdutoSerializer(serializers.ModelSerializer):
    # 1. ATALHO: Em vez de mostrar só o ID da categoria (ex: 1), 
    # ele já traz o nome bonitinho (ex: "Lanches") para facilitar a vida de quem lê.
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    
    # 2. CAMPOS CALCULADOS: Esses campos não existem como colunas "fixas" no banco, 
    # mas o tradutor é esperto e calcula na hora usando as funções que você criou no Model.
    estoque_baixo = serializers.BooleanField(read_only=True)
    margem_lucro = serializers.FloatField(read_only=True)

    class Meta:
        model = Produto
        # Aqui a gente lista exatamente o que quer que apareça na API.
        # Se você esquecer de colocar aqui, a informação não "viaja" para o navegador.
        fields = [
            'id', 'nome', 'categoria', 'categoria_nome',
            'quantidade', 'preco', 'preco_custo', 'estoque_minimo',
            'descricao', 'ativo', 'estoque_baixo', 'margem_lucro',
            'criado_em', 'atualizado_em'
        ]