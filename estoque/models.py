"""
MODELS = As tabelas do banco de dados, escritas em Python
Django converte automaticamente estas classes em SQL.
Você nunca precisa escrever CREATE TABLE!
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

# --- A GAVETA: CATEGORIA ---
class Categoria(models.Model):
    """
    Categoria de produto: Lanches, Bebidas, Salgados, etc.
    Serve para organizar os produtos em grupos.
    """
    nome = models.CharField(max_length=100, unique=True) # unique=True: Não deixa criar dois "Lanches"
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True) # Se a categoria parar de existir, a gente só desativa
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome'] # Organiza de A a Z na tela

    def __str__(self):
        # O que aparece quando o Django precisa mostrar o nome da categoria
        return self.nome


# --- O PRODUTO: A COXINHA, O LANCHE, O REFRIGERANTE ---
class Produto(models.Model):
    """
    Produto no estoque da lanchonete.
    Cada campo aqui vira uma coluna no banco de dados.
    """
    nome = models.CharField(max_length=200, verbose_name='Nome do Produto')
    
    # RELAÇÃO: Diz que o produto pertence a uma categoria.
    # on_delete=models.SET_NULL: Se você apagar a categoria "Lanches", 
    # o X-Bacon não some, ele só fica "sem categoria".
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produtos', # Permite fazer: categoria.produtos.all()
        verbose_name='Categoria'
    )
    
    # ESTOQUE: Quantos tem na prateleira.
    # MinValueValidator(0): Impede que o estoque fique -1 (não existe coxinha negativa!)
    quantidade = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Quantidade em Estoque'
    )
    
    # DINHEIRO: DecimalField é obrigatório para grana.
    # max_digits=8: O número pode ter 8 algarismos no total.
    # decimal_places=2: Sempre duas casas depois da vírgula (centavos).
    preco = models.DecimalField(
        max_digits=8,
        decimal_places=2,
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
    
    # ALERTA: Quando chegar nesse número, o sistema avisa que vai acabar.
    estoque_minimo = models.IntegerField(
        default=5,
        verbose_name='Estoque Mínimo (alerta)'
    )
    
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True) # Salva a hora toda vez que você mexer no produto

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} (R$ {self.preco})'

    # --- AS "SACADAS" DO PROGRAMADOR (Properties) ---

    @property
    def estoque_baixo(self):
        """O SISTEMA PENSA: 'Tô ficando sem mercadoria?'"""
        return self.quantidade <= self.estoque_minimo

    @property
    def margem_lucro(self):
        """O SISTEMA PENSA: 'Tô ganhando quanto nesse lanche?'"""
        # Fórmula: ((Venda - Custo) / Custo) * 100
        if self.preco_custo and self.preco_custo > 0:
            return ((self.preco - self.preco_custo) / self.preco_custo) * 100
        return None

    def pode_vender(self, quantidade):
        """O SISTEMA PENSA: 'Dá pra entregar o que o cliente quer?'"""
        return self.quantidade >= quantidade