from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from datetime import date
from estoque.models import Produto, Categoria
from vendas.models import Venda, ItemVenda
from caixa.models import Caixa
from relatorios.services import gerar_relatorio_excel


# --- TESTE DO "COZINHEIRO" (O Serviço de Excel) ---
class RelatorioServiceTest(TestCase):
    """
    Testa se o motor que fabrica o Excel está funcionando. 
    Aqui a gente nem abre o navegador, testa a função direto no código.
    """

    def setUp(self):
        """
        PREPARAÇÃO: Cria um cenário real no banco de dados de teste.
        Usuário -> Categoria -> Produto -> Venda -> Item da Venda.
        """
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
        """
        TESTE: A função 'gerar_relatorio_excel' consegue criar o arquivo?
        """
        buffer = gerar_relatorio_excel(
            data_inicio=date.today().replace(day=1),
            data_fim=date.today(),
        )
        # O buffer é o arquivo na memória. 
        # Se ele tiver mais de 1000 "letrinhas" (bytes), é porque o Excel foi criado com sucesso.
        self.assertGreater(len(buffer.read()), 1000)

    def test_buffer_e_bytes(self):
        """
        TESTE: O que a função devolve é realmente um "pacotinho de dados" (BytesIO)?
        """
        import io
        buffer = gerar_relatorio_excel()
        self.assertIsInstance(buffer, io.BytesIO)


# --- TESTE DAS "TELAS" (As Views de Relatórios) ---
class RelatorioViewTest(TestCase):
    def setUp(self):
        """Prepara um usuário para tentar logar nas telas."""
        self.user = User.objects.create_user('rv', password='pass')

    def test_painel_requer_login(self):
        """
        SEGURANÇA: Um curioso tentou acessar os relatórios sem logar.
        Ele tem que ser expulso (302 - Redirecionado para o login).
        """
        r = self.client.get(reverse('relatorios:painel'))
        self.assertEqual(r.status_code, 302)

    def test_painel_ok_com_login(self):
        """
        TESTE: O funcionário logou e tentou abrir o painel.
        Tem que aparecer "OK" (Status 200).
        """
        self.client.login(username='rv', password='pass')
        r = self.client.get(reverse('relatorios:painel'))
        self.assertEqual(r.status_code, 200)

    def test_download_excel_retorna_arquivo(self):
        """
        TESTE: Quando clica no botão de Excel, o navegador recebe um arquivo?
        """
        self.client.login(username='rv', password='pass')
        r = self.client.get(reverse('relatorios:excel'))
        self.assertEqual(r.status_code, 200)
        # Verifica se o tipo do que está sendo enviado é uma "Planilha Spreadsheet"
        self.assertIn('spreadsheetml', r['Content-Type'])
        # Verifica se o navegador entendeu que é um "Anexo" (download)
        self.assertIn('attachment', r['Content-Disposition'])

    def test_api_grafico_vendas_7dias(self):
        """
        TESTE: O gráfico pediu dados dos últimos 7 dias.
        A API devolveu os 7 dias certinho em formato JSON?
        """
        self.client.login(username='rv', password='pass')
        r = self.client.get(reverse('relatorios:grafico_api') + '?tipo=vendas_7dias')
        self.assertEqual(r.status_code, 200)
        
        data = r.json() # Transforma a resposta em um dicionário Python
        self.assertIn('dados', data)
        # Tem que ter exatamente 7 registros (um para cada dia da semana)
        self.assertEqual(len(data['dados']), 7)