from django.db import models
from django.contrib.auth.models import User
from estoque.models import Produto
from decimal import Decimal


class Venda(models.Model):
    """
    Uma venda completa (pode ter vários itens).
    Relacionamento: Uma Venda tem muitos ItemVenda
    Isso é chamado de relação One-to-Many (1:N)
    """
    TIPO_PAGAMENTO = [
        ('DINHEIRO', 'Dinheiro'),
        ('CARTAO_CREDITO', 'Cartão de Crédito'),
        ('CARTAO_DEBITO', 'Cartão de Débito'),
        ('PIX', 'PIX'),
        ('FIADO', 'Fiado'),
    ]
    STATUS = [
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
        ('PENDENTE', 'Pendente'),
    ]

    numero = models.AutoField(primary_key=True)          # Número da venda
    cliente_nome = models.CharField(max_length=200, blank=True, verbose_name='Cliente')
    cliente_telefone = models.CharField(max_length=20, blank=True)
    tipo_pagamento = models.CharField(max_length=20, choices=TIPO_PAGAMENTO, default='DINHEIRO')
    status = models.CharField(max_length=20, choices=STATUS, default='CONCLUIDA')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    troco = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    operador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='vendas',
        verbose_name='Operador'
    )
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'
        ordering = ['-criado_em']

    def __str__(self):
        return f'Venda #{self.numero} - R$ {self.total}'

    def calcular_totais(self):
        """Recalcula subtotal e total baseado nos itens"""
        self.subtotal = sum(item.total for item in self.itens.all())
        self.total = self.subtotal - self.desconto
        self.save()


class ItemVenda(models.Model):
    """
    Cada produto dentro de uma venda.
    Guardamos preco_unitario aqui porque o preço pode mudar no futuro,
    mas o histórico deve ser preservado!
    """
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True)
    produto_nome = models.CharField(max_length=200)   # Cópia do nome (histórico)
    quantidade = models.IntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Calcula automaticamente o total antes de salvar
        self.total = self.preco_unitario * self.quantidade
        # Copia o nome do produto para preservar histórico
        if self.produto and not self.produto_nome:
            self.produto_nome = self.produto.nome
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.produto_nome} x{self.quantidade}'
