from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
import json
from estoque.models import Produto, Categoria
from caixa.models import Caixa
from .models import Venda, ItemVenda


class VendaModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('op', password='pass')
        self.venda = Venda.objects.create(
            operador=self.user,
            subtotal=Decimal('25.00'),
            desconto=Decimal('5.00'),
            total=Decimal('20.00'),
            tipo_pagamento='DINHEIRO',
        )

    def test_str_contem_numero_e_total(self):
        s = str(self.venda)
        self.assertIn(str(self.venda.numero), s)

    def test_status_padrao_concluida(self):
        self.assertEqual(self.venda.status, 'CONCLUIDA')


class PDVViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('caixa', password='pass')
        self.cat = Categoria.objects.create(nome='Lanches')
        self.produto = Produto.objects.create(
            nome='X-Test', categoria=self.cat,
            preco=Decimal('10.00'), quantidade=50,
        )
        self.caixa = Caixa.objects.create(
            operador=self.user, valor_inicial=Decimal('100.00'),
        )

    def test_pdv_requer_login(self):
        r = self.client.get(reverse('vendas:pdv'))
        self.assertEqual(r.status_code, 302)

    def test_pdv_carrega_produtos(self):
        self.client.login(username='caixa', password='pass')
        r = self.client.get(reverse('vendas:pdv'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'X-Test')

    def test_finalizar_venda_baixa_estoque(self):
        self.client.login(username='caixa', password='pass')
        itens = json.dumps([{'produto_id': self.produto.pk, 'quantidade': 3}])
        self.client.post(reverse('vendas:finalizar'), {
            'itens': itens,
            'tipo_pagamento': 'DINHEIRO',
            'desconto': '0',
            'troco': '0',
        })
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.quantidade, 47)

    def test_finalizar_venda_cria_registro(self):
        self.client.login(username='caixa', password='pass')
        qtd_antes = Venda.objects.count()
        itens = json.dumps([{'produto_id': self.produto.pk, 'quantidade': 2}])
        self.client.post(reverse('vendas:finalizar'), {
            'itens': itens, 'tipo_pagamento': 'PIX',
            'desconto': '0', 'troco': '0',
        })
        self.assertEqual(Venda.objects.count(), qtd_antes + 1)

    def test_finalizar_sem_caixa_redireciona(self):
        self.caixa.status = 'FECHADO'
        self.caixa.save()
        self.client.login(username='caixa', password='pass')
        itens = json.dumps([{'produto_id': self.produto.pk, 'quantidade': 1}])
        r = self.client.post(reverse('vendas:finalizar'), {
            'itens': itens, 'tipo_pagamento': 'DINHEIRO',
            'desconto': '0', 'troco': '0',
        })
        self.assertEqual(r.status_code, 302)
        # Estoque não deve ter mudado
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.quantidade, 50)
