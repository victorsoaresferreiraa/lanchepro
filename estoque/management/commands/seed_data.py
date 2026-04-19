"""
MANAGEMENT COMMAND = Um comando personalizado que você roda no terminal.
Assim como 'python manage.py migrate', você rodará:
'python manage.py seed_data'

Ele cria dados iniciais para testar o sistema.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from estoque.models import Produto, Categoria
from clientes.models import Cliente, ContaAberta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados iniciais de exemplo'

    def handle(self, *args, **options):
        # Mensagem inicial no terminal para você saber que começou
        self.stdout.write('🍔 Iniciando seed de dados...\n')

        # ==============================
        # 1. USUÁRIO ADMIN (O Dono da Loja)
        # ==============================
        # Se não existir um 'admin', ele cria um com senha 'admin123'
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                password='admin123',
                email='admin@lanchopro.com',
                first_name='Administrador'
            )
            self.stdout.write(self.style.SUCCESS('✅ Usuário admin criado (senha: admin123)'))
        else:
            self.stdout.write('⚠️  Usuário admin já existe')

        # ==============================
        # 2. CATEGORIAS (As Gavetas)
        # ==============================
        categorias_data = [
            ('Lanches', 'Hambúrgueres, sanduíches e afins'),
            ('Bebidas', 'Refrigerantes, sucos e água'),
            ('Salgados', 'Coxinha, esfiha, pão de queijo'),
            ('Sobremesas', 'Doces, sorvetes e açaí'),
            ('Combos', 'Combinações especiais'),
            ('Porções', 'Batata frita e aperitivos'),
        ]
        categorias = {}
        for nome, desc in categorias_data:
            # get_or_create: Se já existir, ele só pega. Se não, ele cria.
            cat, created = Categoria.objects.get_or_create(nome=nome, defaults={'descricao': desc})
            categorias[nome] = cat
            if created:
                self.stdout.write(f'  📁 Categoria criada: {nome}')

        # ==============================
        # 3. PRODUTOS (O Cardápio)
        # ==============================
        produtos_data = [
            # (nome, categoria, qtd_estoque, preco_venda, preco_custo, estoque_minimo)
            ('X-Burguer', 'Lanches', 50, Decimal('12.00'), Decimal('5.50'), 5),
            ('X-Salada', 'Lanches', 50, Decimal('13.00'), Decimal('6.00'), 5),
            ('X-Bacon', 'Lanches', 40, Decimal('15.00'), Decimal('7.00'), 5),
            ('Coca-Cola Lata', 'Bebidas', 100, Decimal('5.00'), Decimal('2.20'), 10),
            ('Coxinha', 'Salgados', 60, Decimal('4.00'), Decimal('1.50'), 10),
            ('Açaí 300ml', 'Sobremesas', 25, Decimal('12.00'), Decimal('5.00'), 5),
        ]

        criados = 0
        for nome, cat_nome, qtd, preco, custo, estoque_min in produtos_data:
            _, created = Produto.objects.get_or_create(
                nome=nome,
                defaults={
                    'categoria': categorias[cat_nome],
                    'quantidade': qtd,
                    'preco': preco,
                    'preco_custo': custo,
                    'estoque_minimo': estoque_min,
                }
            )
            if created:
                criados += 1

        self.stdout.write(self.style.SUCCESS(f'✅ {criados} produtos criados'))

        # ==============================
        # 4. CLIENTES E "FIADO" (Os Devedores)
        # ==============================
        clientes_data = [
            ('João Silva', '(11) 98765-4321'),
            ('Maria Santos', '(11) 97654-3210'),
        ]
        for nome, tel in clientes_data:
            cliente, created = Cliente.objects.get_or_create(
                nome=nome,
                defaults={'telefone': tel}
            )
            if created:
                # Já cria uma dívida de exemplo para testar o sistema de "Fiado"
                ContaAberta.objects.create(
                    cliente=cliente,
                    descricao='2x X-Burguer + 2x Coca-Cola',
                    total=Decimal('34.00'),
                )
                self.stdout.write(f'  👤 Cliente criado: {nome}')

        # ==============================
        # RESUMO FINAL (O Recibo do Comando)
        # ==============================
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('🎉 Seed concluído com sucesso!\n'))
        self.stdout.write('📋 Dados criados:')
        self.stdout.write(f'   Produtos: {Produto.objects.count()}')
        self.stdout.write(f'   Categorias: {Categoria.objects.count()}')
        self.stdout.write(f'   Clientes: {Cliente.objects.count()}')
        self.stdout.write('\n🔑 Acesso:')
        self.stdout.write('   Usuário: admin | Senha: admin123')
        self.stdout.write('='*50 + '\n')