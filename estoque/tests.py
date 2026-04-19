from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from .models import Produto, Categoria

# --- TESTES DO CORAÇÃO DO PRODUTO (Lógica Interna) ---
class ProdutoModelTest(TestCase):
    def setUp(self):
        """
        PREPARAÇÃO: Cria um lanche de teste com preço de venda e preço de custo.
        """
        self.cat = Categoria.objects.create(nome="Lanches")
        self.produto = Produto.objects.create(
            nome="X-Burguer", 
            categoria=self.cat,
            preco=Decimal("12.00"),       # Venda
            preco_custo=Decimal("5.00"),   # Quanto custou fazer
            quantidade=10, 
            estoque_minimo=5,
        )

    def test_str_contem_nome(self):
        """O nome do produto tem que aparecer quando a gente der um print nele."""
        self.assertIn("X-Burguer", str(self.produto))

    def test_estoque_baixo_alerta(self):
        """
        TESTE DO ALERTA: Se o estoque chegar no mínimo (5) ou abaixo disso (2),
        o sistema tem que avisar que está baixo.
        """
        # Teste 1: Igual ao mínimo
        self.produto.quantidade = 5
        self.assertTrue(self.produto.estoque_baixo)
        
        # Teste 2: Abaixo do mínimo
        self.produto.quantidade = 2
        self.assertTrue(self.produto.estoque_baixo)

    def test_estoque_ok_acima_minimo(self):
        """Se eu tenho 10 e o mínimo é 5, o alerta tem que estar desligado."""
        self.produto.quantidade = 10
        self.assertFalse(self.produto.estoque_baixo)

    def test_margem_lucro(self):
        """
        TESTE DA MATEMÁTICA: (12 - 5) / 5 * 100 = 140% de lucro.
        O sistema tem que saber fazer essa conta sozinho.
        """
        self.assertAlmostEqual(self.produto.margem_lucro, 140.0, places=1)

    def test_pode_vender_estoque(self):
        """
        TESTE DO PODE VENDER: 
        - Posso vender 5 se tenho 10? Sim.
        - Posso vender 10 se tenho 10? Sim.
        - Posso vender 15 se tenho 10? NÃO!
        """
        self.assertTrue(self.produto.pode_vender(5))
        self.assertTrue(self.produto.pode_vender(10))
        self.assertFalse(self.produto.pode_vender(15))


# --- TESTES DAS TELAS DE ESTOQUE (Interface) ---
class EstoqueViewTest(TestCase):
    def setUp(self):
        """Cria um usuário e uma Coca-Cola de teste."""
        self.user = User.objects.create_user('test', password='pass123')
        self.cat = Categoria.objects.create(nome="Bebidas")
        self.produto = Produto.objects.create(
            nome="Coca-Cola", categoria=self.cat,
            preco=Decimal("5.00"), quantidade=20, estoque_minimo=5,
        )

    def test_lista_bloqueada_sem_login(self):
        """Ninguém mexe no estoque sem estar logado!"""
        r = self.client.get(reverse('estoque:lista'))
        self.assertEqual(r.status_code, 302)

    def test_soft_delete(self):
        """
        TESTE DO 'DELETAR SEM SUMIR': 
        A gente não apaga o produto do banco, só marca como 'ativo=False'.
        Isso é importante para não estragar o histórico de vendas antigas.
        """
        self.client.login(username='test', password='pass123')
        self.client.post(reverse('estoque:excluir', args=[self.produto.pk]))
        
        self.produto.refresh_from_db()
        self.assertFalse(self.produto.ativo) # Agora está desativado
        self.assertTrue(Produto.objects.filter(pk=self.produto.pk).exists()) # Mas ainda existe no banco

    def test_ajustar_estoque(self):
        """
        TESTE DO AJUSTE: Se eu chegar com uma caixa nova (adicionar) 
        ou se uma Coca estourar (remover), o saldo tem que bater.
        """
        self.client.login(username='test', password='pass123')
        
        # 1. Adicionando 10 (20 + 10 = 30)
        self.client.post(reverse('estoque:ajustar', args=[self.produto.pk]),
                         {'tipo': 'adicionar', 'quantidade': 10})
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.quantidade, 30)

        # 2. Removendo 5 (30 - 5 = 25) — Ops, o teste original remove do valor inicial 20.
        # Vamos seguir a lógica do seu código:
        self.client.post(reverse('estoque:ajustar', args=[self.produto.pk]),
                         {'tipo': 'remover', 'quantidade': 5})
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.quantidade, 25)

    def test_ajustar_remover_sem_estoque_falha(self):
        """O sistema não pode deixar eu remover 999 Cocas se eu só tenho 20."""
        self.client.login(username='test', password='pass123')
        self.client.post(reverse('estoque:ajustar', args=[self.produto.pk]),
                         {'tipo': 'remover', 'quantidade': 999})
        self.produto.refresh_from_db()
        # Tem que continuar 20, porque a operação deve ser cancelada.
        self.assertEqual(self.produto.quantidade, 20)