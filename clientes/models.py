from django.db import models
from decimal import Decimal


class Cliente(models.Model):
    nome = models.CharField(max_length=200)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    endereco = models.TextField(blank=True)
    observacoes = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cliente'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def divida_total(self):
        return self.contas.filter(pago=False).aggregate(
            total=models.Sum('total')
        )['total'] or Decimal('0')


class ContaAberta(models.Model):
    """Venda fiado - o cliente deve pagar depois"""
    STATUS = [
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
        ('VENCIDO', 'Vencido'),
        ('PARCIAL', 'Parcial'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='contas')
    descricao = models.TextField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_vencimento = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='PENDENTE')
    pago = models.BooleanField(default=False)
    data_pagamento = models.DateTimeField(null=True, blank=True)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.cliente.nome} - R$ {self.total} ({self.status})'

    @property
    def saldo_devedor(self):
        return self.total - self.valor_pago
