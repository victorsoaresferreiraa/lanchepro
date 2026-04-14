from django.db import models
from django.contrib.auth.models import User


class Caixa(models.Model):
    STATUS = [('ABERTO', 'Aberto'), ('FECHADO', 'Fechado')]

    operador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    data_abertura = models.DateTimeField(auto_now_add=True)
    data_fechamento = models.DateTimeField(null=True, blank=True)
    valor_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    valor_vendas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_sangria = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_reforco = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_final = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS, default='ABERTO')
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Caixa'
        ordering = ['-data_abertura']

    def __str__(self):
        return f'Caixa {self.data_abertura.strftime("%d/%m/%Y")} - {self.status}'

    @property
    def saldo_esperado(self):
        return self.valor_inicial + self.valor_vendas + self.valor_reforco - self.valor_sangria


class MovimentacaoCaixa(models.Model):
    TIPO = [
        ('VENDA', 'Venda'),
        ('SANGRIA', 'Sangria'),
        ('REFORCO', 'Reforço'),
        ('ABERTURA', 'Abertura'),
        ('FECHAMENTO', 'Fechamento'),
        ('PAGAMENTO_FIADO', 'Pagamento Fiado'),
    ]

    caixa = models.ForeignKey(Caixa, on_delete=models.CASCADE, related_name='movimentacoes')
    tipo = models.CharField(max_length=20, choices=TIPO)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField(blank=True)
    operador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_hora']

    def __str__(self):
        return f'{self.tipo} - R$ {self.valor}'
