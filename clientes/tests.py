from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from .models import Cliente, ContaAberta


class ClienteModelTest(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(nome="João Silva", telefone="11999")
        self.conta = ContaAberta.objects.create(
            cliente=self.cliente, descricao="2x X-Burguer",
            total=Decimal("24.00"), valor_pago=Decimal("10.00"),
        )

    def test_str_retorna_nome(self):
        self.assertEqual(str(self.cliente), "João Silva")

    def test_saldo_devedor(self):
        self.assertEqual(self.conta.saldo_devedor, Decimal("14.00"))

    def test_divida_total_cliente(self):
        self.assertEqual(self.cliente.divida_total, Decimal("24.00"))

    def test_quitado_nao_conta_divida(self):
        self.conta.pago = True
        self.conta.valor_pago = self.conta.total
        self.conta.save()
        self.assertEqual(self.cliente.divida_total, Decimal("0"))


class ClienteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('u', password='p')
        self.cliente = Cliente.objects.create(nome="Maria")

    def test_lista_requer_login(self):
        r = self.client.get(reverse('clientes:lista'))
        self.assertEqual(r.status_code, 302)

    def test_lista_acessivel(self):
        self.client.login(username='u', password='p')
        r = self.client.get(reverse('clientes:lista'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Maria")

    def test_registrar_pagamento(self):
        conta = ContaAberta.objects.create(
            cliente=self.cliente, descricao="teste",
            total=Decimal("50.00"),
        )
        self.client.login(username='u', password='p')
        self.client.post(reverse('clientes:pagar', args=[conta.pk]), {'valor': '50.00'})
        conta.refresh_from_db()
        self.assertTrue(conta.pago)
        self.assertEqual(conta.status, 'PAGO')
