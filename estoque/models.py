"""
MODELS = As tabelas do banco de dados, escritas em Python
Django converte automaticamente estas classes em SQL.
Você nunca precisa escrever CREATE TABLE!
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Categoria(models.Model):
    """Categoria de produto: Lanches, Bebidas, Salgados, etc."""
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Produto(models.Model):
    """
    Produto no estoque da lanchonete.
    Cada campo aqui vira uma coluna no banco de dados.
    """
    nome = models.CharField(max_length=200, verbose_name='Nome do Produto')
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,  # Se apagar categoria, produto fica sem categoria
        null=True,
        blank=True,
        related_name='produtos',    # produto.categoria / categoria.produtos.all()
        verbose_name='Categoria'
    )
    quantidade = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],  # Não pode ser negativo
        verbose_name='Quantidade em Estoque'
    )
    preco = models.DecimalField(
        max_digits=8,
        decimal_places=2,          # Ex: 9.99 → até R$999.999,99
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Preço de Venda (R$)'
    )
    preco_custo = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Preço de Custo (R$)'
    )
    estoque_minimo = models.IntegerField(
        default=5,
        verbose_name='Estoque Mínimo (alerta)'
    )
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)  # Atualiza automaticamente

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} (R$ {self.preco})'

    @property
    def estoque_baixo(self):
        """Retorna True se estoque está abaixo do mínimo"""
        return self.quantidade <= self.estoque_minimo

    @property
    def margem_lucro(self):
        """Calcula margem de lucro percentual"""
        if self.preco_custo and self.preco_custo > 0:
            return ((self.preco - self.preco_custo) / self.preco_custo) * 100
        return None

    def pode_vender(self, quantidade):
        """Verifica se tem estoque suficiente"""
        return self.quantidade >= quantidade
