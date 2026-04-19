from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
import json
from estoque.models import Produto, Categoria
from caixa.models import Caixa
from .models import Venda, ItemVenda

# --- TESTES DO MODELO (A estrutura do Banco de Dados) ---
class VendaModelTest(TestCase):
    def setUp(self):
        """
        PREPARAÇÃO: Cria um cenário de mentira antes de testar.
        Cria um usuário e uma venda fake para a gente brincar.
        """
        self.user = User.objects.create_user('op', password='pass')
        self.venda = Venda.objects.create(
            operador=self.user,
            subtotal=Decimal('25.00'),
            desconto=Decimal('5.00'),
            total=Decimal('20.00'),
            tipo_pagamento='DINHEIRO',
        )

    def test_str_contem_numero_e_total(self):
        """
        TESTE: Se eu mandar imprimir a venda, ela mostra o número dela?
        """
        s = str(self.venda)
        self.assertIn(str(self.venda.numero), s)

    def test_status_padrao_concluida(self):
        """
        TESTE: Quando eu crio uma venda, ela já nasce com status 'CONCLUIDA'?
        """
        self.assertEqual(self.venda.status, 'CONCLUIDA')


# --- TESTES DAS VIEWS (As telas e a lógica do sistema) ---
class PDVViewTest(TestCase):
    def setUp(self):
        """
        Cria um ambiente completo: Usuário, Categoria, Produto e um Caixa Aberto.
        """
        self.user = User.objects.create_user('caixa', password='pass')
        self.cat = Categoria.objects.create(nome='Lanches')
        self.produto = Produto.objects.create(
            nome='X-Test', categoria=self.cat,
            preco=Decimal('10.00'), quantidade=50, # Começamos com 50 no estoque
        )
        self.caixa = Caixa.objects.create(
            operador=self.user, valor_inicial=Decimal('100.00'),
            status='ABERTO' # Caixa começa aberto para os testes
        )

    def test_pdv_requer_login(self):
        """
        SEGURANÇA: Se um hacker tentar entrar no PDV sem logar, 
        ele tem que ser expulso (status 302 é redirecionamento).
        """
        r = self.client.get(reverse('vendas:pdv'))
        self.assertEqual(r.status_code, 302)

    def test_pdv_carrega_produtos(self):
        """
        INTERFACE: Se eu logar, a tela do PDV tem que carregar 
        e mostrar o nome do produto 'X-Test'.
        """
        self.client.login(username='caixa', password='pass')
        r = self.client.get(reverse('vendas:pdv'))
        self.assertEqual(r.status_code, 200) # 200 = Sucesso!
        self.assertContains(r, 'X-Test')

    def test_finalizar_venda_baixa_estoque(self):
        """
        LOGICA: Se eu vender 3 itens, o estoque tem que diminuir!
        De 50 tem que ir para 47. Se não for, o sistema está roubando.
        """
        self.client.login(username='caixa', password='pass')
        # Simula o carrinho de compras com 3 unidades
        itens = json.dumps([{'produto_id': self.produto.pk, 'quantidade': 3}])
        
        self.client.post(reverse('vendas:finalizar'), {
            'itens': itens,
            'tipo_pagamento': 'DINHEIRO',
            'desconto': '0',
            'troco': '0',
        })
        
        # 'refresh_from_db' serve para o Python ir no banco ver o valor atualizado
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.quantidade, 47)

    def test_finalizar_venda_cria_registro(self):
        """
        BANCO DE DADOS: Verifica se o sistema realmente salvou a venda no banco.
        """
        self.client.login(username='caixa', password='pass')
        qtd_antes = Venda.objects.count() # Conta quantas vendas tinha
        itens = json.dumps([{'produto_id': self.produto.pk, 'quantidade': 2}])
        
        self.client.post(reverse('vendas:finalizar'), {
            'itens': itens, 'tipo_pagamento': 'PIX',
            'desconto': '0', 'troco': '0',
        })
        
        # Agora tem que ter a quantidade que tinha antes + 1
        self.assertEqual(Venda.objects.count(), qtd_antes + 1)

    def test_finalizar_sem_caixa_redireciona(self):
        """
        REGRA DE NEGÓCIO: Se o caixa estiver FECHADO, o sistema NÃO PODE vender.
        O estoque tem que continuar igual (50).
        """
        self.caixa.status = 'FECHADO'
        self.caixa.save()
        
        self.client.login(username='caixa', password='pass')
        itens = json.dumps([{'produto_id': self.produto.pk, 'quantidade': 1}])
        
        r = self.client.post(reverse('vendas:finalizar'), {
            'itens': itens, 'tipo_pagamento': 'DINHEIRO',
            'desconto': '0', 'troco': '0',
        })
        
        # Tem que ser redirecionado (302) e o estoque não pode ter mudado
        self.assertEqual(r.status_code, 302)
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.quantidade, 50)