from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from datetime import date
from estoque.models import Produto, Categoria
from vendas.models import Venda, ItemVenda
from caixa.models import Caixa
from relatorios.services import gerar_relatorio_excel


class RelatorioServiceTest(TestCase):
    """Testa a geração do Excel sem HTTP — testa o serviço diretamente."""

    def setUp(self):
        self.user = User.objects.create_user('rel_user', password='pass')
        cat = Categoria.objects.create(nome="Lanches")
        prod = Produto.objects.create(
            nome="X-Test", categoria=cat,
            preco=Decimal("12.00"), quantidade=50,
        )
        venda = Venda.objects.create(
            operador=self.user,
            subtotal=Decimal("24.00"),
            total=Decimal("24.00"),
            tipo_pagamento="DINHEIRO",
        )
        ItemVenda.objects.create(
            venda=venda, produto=prod, produto_nome=prod.nome,
            quantidade=2, preco_unitario=Decimal("12.00"),
        )

    def test_gera_excel_sem_erro(self):
        """A geração do Excel deve rodar sem lançar exceção."""
        buffer = gerar_relatorio_excel(
            data_inicio=date.today().replace(day=1),
            data_fim=date.today(),
        )
        # Buffer deve ter conteúdo (arquivo Excel real)
        self.assertGreater(len(buffer.read()), 1000)

    def test_buffer_e_bytes(self):
        """Buffer deve ser um BytesIO."""
        import io
        buffer = gerar_relatorio_excel()
        self.assertIsInstance(buffer, io.BytesIO)


class RelatorioViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('rv', password='pass')

    def test_painel_requer_login(self):
        r = self.client.get(reverse('relatorios:painel'))
        self.assertEqual(r.status_code, 302)

    def test_painel_ok_com_login(self):
        self.client.login(username='rv', password='pass')
        r = self.client.get(reverse('relatorios:painel'))
        self.assertEqual(r.status_code, 200)

    def test_download_excel_retorna_arquivo(self):
        self.client.login(username='rv', password='pass')
        r = self.client.get(reverse('relatorios:excel'))
        self.assertEqual(r.status_code, 200)
        self.assertIn('spreadsheetml', r['Content-Type'])
        self.assertIn('attachment', r['Content-Disposition'])

    def test_api_grafico_vendas_7dias(self):
        self.client.login(username='rv', password='pass')
        r = self.client.get(reverse('relatorios:grafico_api') + '?tipo=vendas_7dias')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('dados', data)
        self.assertEqual(len(data['dados']), 7)
