from django.db import models
from django.contrib.auth.models import User
from estoque.models import Produto
from decimal import Decimal

# --- A TABELA PAI: A VENDA ---
class Venda(models.Model):
    """
    Aqui é o cabeçalho do pedido. Pense na nota fiscal: 
    é a parte de cima que diz quem comprou e como pagou.
    """
    # Opções de pagamento (as caixinhas de seleção)
    TIPO_PAGAMENTO = [
        ('DINHEIRO', 'Dinheiro'),
        ('CARTAO_CREDITO', 'Cartão de Crédito'),
        ('CARTAO_DEBITO', 'Cartão de Débito'),
        ('PIX', 'PIX'),
        ('FIADO', 'Fiado'),
    ]
    # Situação da venda
    STATUS = [
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
        ('PENDENTE', 'Pendente'),
    ]

    # Campos de identificação
    numero = models.AutoField(primary_key=True) # Cria 1, 2, 3... sozinho
    cliente_nome = models.CharField(max_length=200, blank=True, verbose_name='Cliente')
    cliente_telefone = models.CharField(max_length=20, blank=True)
    
    # Regras de negócio
    tipo_pagamento = models.CharField(max_length=20, choices=TIPO_PAGAMENTO, default='DINHEIRO')
    status = models.CharField(max_length=20, choices=STATUS, default='CONCLUIDA')
    
    # Valores financeiros (DecimalField é para dinheiro, nunca use Float!)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    troco = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Quem fez a venda. Se o usuário for deletado, a venda fica com 'null' mas não some.
    operador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='vendas',
        verbose_name='Operador'
    )
    
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True) # Salva a data e hora na hora que criar

    class Meta:
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'
        ordering = ['-criado_em'] # As vendas mais novas aparecem primeiro

    def __str__(self):
        return f'Venda #{self.numero} - R$ {self.total}'

    def calcular_totais(self):
        """
        O Calculador: Vai lá nos itens, soma tudo, tira o desconto e atualiza o total.
        """
        self.subtotal = sum(item.total for item in self.itens.all())
        self.total = self.subtotal - self.desconto
        self.save()


# --- A TABELA FILHA: OS ITENS DA VENDA ---
class ItemVenda(models.Model):
    """
    Aqui são as linhas da nota fiscal. 
    Se você comprou 3 coxinhas, essa tabela registra isso.
    """
    # A venda a que este item pertence (CASCADE: se apagar a venda, apaga os itens)
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens')
    
    # Qual é o produto. SET_NULL: se o produto for excluído da loja, a venda continua existindo.
    produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True)
    
    # DICA DE MESTRE: Guardamos o nome e o preço aqui também!
    # Por que? Porque se amanha você mudar o preço do produto no estoque, 
    # a venda de ontem tem que continuar com o preço antigo.
    produto_nome = models.CharField(max_length=200) 
    quantidade = models.IntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        """
        O 'Faz-Tudo' antes de salvar:
        Calcula o total da linha e copia o nome do produto para o histórico.
        """
        self.total = self.preco_unitario * self.quantidade
        
        # Garante que o nome do produto fique gravado "em pedra"
        if self.produto and not self.produto_nome:
            self.produto_nome = self.produto.nome
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.produto_nome} x{self.quantidade}'