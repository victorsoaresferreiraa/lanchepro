from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from .models import Caixa, MovimentacaoCaixa


class CaixaModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('op', password='pass')
        self.caixa = Caixa.objects.create(
            operador=self.user,
            valor_inicial=Decimal("200.00"),
            valor_vendas=Decimal("500.00"),
            valor_sangria=Decimal("100.00"),
            valor_reforco=Decimal("50.00"),
        )

    def test_saldo_esperado(self):
        # 200 + 500 + 50 - 100 = 650
        self.assertEqual(self.caixa.saldo_esperado, Decimal("650.00"))

    def test_status_padrao_aberto(self):
        self.assertEqual(self.caixa.status, 'ABERTO')

    def test_str_contem_data(self):
        s = str(self.caixa)
        self.assertIn('ABERTO', s)


class CaixaViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('op2', password='pass')

    def test_abrir_caixa(self):
        self.client.login(username='op2', password='pass')
        r = self.client.post(reverse('caixa:abrir'), {'valor_inicial': '150.00'})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Caixa.objects.filter(status='ABERTO').exists())

    def test_nao_abre_dois_caixas(self):
        Caixa.objects.create(operador=self.user, valor_inicial=Decimal("100"))
        self.client.login(username='op2', password='pass')
        r = self.client.post(reverse('caixa:abrir'), {'valor_inicial': '200.00'})
        self.assertEqual(Caixa.objects.filter(status='ABERTO').count(), 1)
