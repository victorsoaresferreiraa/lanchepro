from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from .models import Produto, Categoria


class ProdutoModelTest(TestCase):
    def setUp(self):
        self.cat = Categoria.objects.create(nome="Lanches")
        self.produto = Produto.objects.create(
            nome="X-Burguer", categoria=self.cat,
            preco=Decimal("12.00"), preco_custo=Decimal("5.00"),
            quantidade=10, estoque_minimo=5,
        )

    def test_str_contem_nome(self):
        self.assertIn("X-Burguer", str(self.produto))

    def test_estoque_baixo_igual_minimo(self):
        self.produto.quantidade = 5
        self.assertTrue(self.produto.estoque_baixo)

    def test_estoque_baixo_abaixo_minimo(self):
        self.produto.quantidade = 2
        self.assertTrue(self.produto.estoque_baixo)

    def test_estoque_ok_acima_minimo(self):
        self.produto.quantidade = 10
        self.assertFalse(self.produto.estoque_baixo)

    def test_margem_lucro(self):
        # (12 - 5) / 5 * 100 = 140%
        self.assertAlmostEqual(self.produto.margem_lucro, 140.0, places=1)

    def test_margem_none_sem_custo(self):
        self.produto.preco_custo = None
        self.assertIsNone(self.produto.margem_lucro)

    def test_pode_vender_suficiente(self):
        self.assertTrue(self.produto.pode_vender(5))

    def test_nao_pode_vender_insuficiente(self):
        self.assertFalse(self.produto.pode_vender(15))

    def test_pode_vender_exato(self):
        self.assertTrue(self.produto.pode_vender(10))


class EstoqueViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', password='pass123')
        self.cat = Categoria.objects.create(nome="Bebidas")
        self.produto = Produto.objects.create(
            nome="Coca-Cola", categoria=self.cat,
            preco=Decimal("5.00"), quantidade=20, estoque_minimo=5,
        )

    def test_lista_redireciona_sem_login(self):
        r = self.client.get(reverse('estoque:lista'))
        self.assertEqual(r.status_code, 302)

    def test_lista_ok_com_login(self):
        self.client.login(username='test', password='pass123')
        r = self.client.get(reverse('estoque:lista'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Coca-Cola")

    def test_criar_produto_valido(self):
        self.client.login(username='test', password='pass123')
        r = self.client.post(reverse('estoque:criar'), {
            'nome': 'X-Bacon', 'categoria': self.cat.pk,
            'preco': '15.00', 'quantidade': 30,
            'estoque_minimo': 5, 'descricao': '',
        })
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Produto.objects.filter(nome='X-Bacon').exists())

    def test_soft_delete(self):
        self.client.login(username='test', password='pass123')
        self.client.post(reverse('estoque:excluir', args=[self.produto.pk]))
        self.produto.refresh_from_db()
        self.assertFalse(self.produto.ativo)
        self.assertTrue(Produto.objects.filter(pk=self.produto.pk).exists())

    def test_ajustar_adicionar(self):
        self.client.login(username='test', password='pass123')
        self.client.post(reverse('estoque:ajustar', args=[self.produto.pk]),
                         {'tipo': 'adicionar', 'quantidade': 10})
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.quantidade, 30)

    def test_ajustar_remover(self):
        self.client.login(username='test', password='pass123')
        self.client.post(reverse('estoque:ajustar', args=[self.produto.pk]),
                         {'tipo': 'remover', 'quantidade': 5})
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.quantidade, 15)

    def test_ajustar_remover_excesso_falha(self):
        self.client.login(username='test', password='pass123')
        self.client.post(reverse('estoque:ajustar', args=[self.produto.pk]),
                         {'tipo': 'remover', 'quantidade': 999})
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.quantidade, 20)
