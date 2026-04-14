# 🍔 LanchoPro — Sistema Web de Gestão de Lanchonete

Sistema **full stack profissional** em Python/Django para gestão completa de lanchonetes.

---

## 🧠 Como um Sistema Web Funciona (Do Zero)

```
NAVEGADOR                    SERVIDOR DJANGO
─────────                    ───────────────
Usuário acessa               urls.py decide qual view chamar
/estoque/         ──────►    views.py busca dados nos models
                             models.py faz query no banco SQLite
                  ◄──────    template HTML é montado e enviado
Página aparece               
```

### As 4 Camadas do Django (MTV)

| Camada | Arquivo | Responsabilidade |
|--------|---------|-----------------|
| **M**odel | `models.py` | Define o banco de dados |
| **T**emplate | `templates/*.html` | O HTML que o usuário vê |
| **V**iew | `views.py` | A lógica de negócio |
| URLs | `urls.py` | Mapeia endereço → view |

---

## 🚀 Rodando Localmente (Do Zero)

### 1. Pré-requisitos
```bash
python --version   # Precisa de Python 3.10+
pip --version      # Gerenciador de pacotes Python
```

### 2. Instalar e rodar
```bash
# Clone ou extraia o projeto
cd lanchonete_web

# Crie um ambiente virtual (isola as dependências)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Instale as dependências
pip install -r requirements.txt

# Crie as tabelas no banco de dados
python manage.py migrate

# Popule com dados de exemplo
python manage.py seed_data

# Inicie o servidor
python manage.py runserver
```

### 3. Acessar
- **Sistema**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin/
- **API REST**: http://localhost:8000/api/estoque/produtos/
- **Login**: admin / admin123

---

## 🐳 Rodando com Docker (Recomendado para Produção)

```bash
# Construir e iniciar
docker compose up -d

# Ver logs em tempo real
docker compose logs -f

# Parar
docker compose down
```

---

## ☁️ Deploy Gratuito no Railway

O Railway é uma plataforma de hosting gratuita para projetos Django.

### Passo a Passo:

**1. Crie conta em** https://railway.app

**2. Instale o CLI:**
```bash
npm install -g @railway/cli
railway login
```

**3. No diretório do projeto:**
```bash
railway init          # Cria projeto no Railway
railway up            # Faz o deploy!
railway domain        # Gera um domínio público
```

**4. Configure as variáveis de ambiente no painel Railway:**
```
SECRET_KEY=sua-chave-secreta-longa
DEBUG=False
ALLOWED_HOSTS=seuapp.railway.app
```

---

## ☁️ Deploy Gratuito no Render

**1. Crie conta em** https://render.com

**2. Crie "New Web Service"**

**3. Configure:**
- Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- Start Command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

**4. Adicione variáveis de ambiente:**
```
SECRET_KEY=sua-chave-secreta
DEBUG=False
ALLOWED_HOSTS=.onrender.com
```

---

## 📡 API REST

O sistema expõe uma API REST completa:

```bash
# Listar produtos
GET /api/estoque/produtos/

# Criar produto
POST /api/estoque/produtos/
Content-Type: application/json
{"nome": "X-Bacon", "preco": "15.00", "quantidade": 50}

# Métricas do dashboard
GET /api/dashboard/metricas/

# Histórico de vendas
GET /api/vendas/

# Clientes e fiado
GET /api/clientes/
```

---

## 🏗️ Estrutura do Projeto

```
lanchonete_web/
├── config/                 ← Configuração central
│   ├── settings.py         ← Todas as configurações Django
│   ├── urls.py             ← Mapa de rotas principal
│   └── wsgi.py             ← Interface com servidor web
│
├── estoque/                ← App de produtos e estoque
│   ├── models.py           ← Produto, Categoria (tabelas DB)
│   ├── views.py            ← Lista, cria, edita produtos
│   ├── serializers.py      ← Converte para JSON (API)
│   ├── api_views.py        ← Endpoints REST
│   ├── forms.py            ← Formulários Django
│   ├── urls.py             ← Rotas HTML
│   ├── api_urls.py         ← Rotas API
│   └── management/commands/seed_data.py  ← Dados iniciais
│
├── vendas/                 ← PDV e histórico de vendas
├── caixa/                  ← Abertura/fechamento/sangria
├── clientes/               ← Fiado e contas em aberto
├── dashboard/              ← Métricas e relatórios
│
├── templates/              ← Todos os HTMLs
│   ├── base.html           ← Layout base (sidebar + topbar)
│   ├── auth/login.html     ← Tela de login
│   ├── dashboard/          ← Dashboard com métricas
│   ├── estoque/            ← CRUD de produtos
│   ├── vendas/             ← PDV e recibo
│   ├── caixa/              ← Controle de caixa
│   └── clientes/           ← Gestão de fiado
│
├── data/                   ← Banco de dados SQLite
├── requirements.txt        ← Dependências Python
├── Dockerfile              ← Para Docker
├── docker-compose.yml      ← Para Docker Compose
└── .env.example            ← Variáveis de ambiente
```

---

## 🔧 Conceitos Que Você Aprendeu

### 1. ORM Django (Object-Relational Mapping)
```python
# Em vez de escrever SQL:
# SELECT * FROM estoque_produto WHERE ativo = TRUE

# Você escreve Python:
Produto.objects.filter(ativo=True)

# Joins automáticos com select_related:
Produto.objects.select_related('categoria').filter(ativo=True)
```

### 2. Views Baseadas em Função
```python
@login_required               # Decorator: bloqueia se não logado
def lista_produtos(request):  # Recebe o HTTP request
    produtos = Produto.objects.all()  # Busca no banco
    return render(request, 'estoque/lista.html', {  # Monta HTML
        'produtos': produtos  # Envia dados para o template
    })
```

### 3. Template Tags Django
```html
{% for produto in produtos %}      <!-- Loop -->
    {{ produto.nome }}             <!-- Exibe variável -->
    {% if produto.estoque_baixo %} <!-- Condição -->
        ⚠️ Estoque baixo!
    {% endif %}
{% endfor %}
{% url 'estoque:lista' %}          <!-- Gera URL sem hardcode -->
```

### 4. API REST com DRF
```python
# ViewSet = CRUD automático completo com 5 linhas!
class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
```

### 5. Transações Atômicas
```python
@transaction.atomic  # Se qualquer linha falhar, reverte TUDO
def finalizar_venda(request):
    venda = Venda.objects.create(...)  # Cria venda
    for item in itens:
        produto.quantidade -= qtd  # Baixa estoque
        produto.save()
    # Se a venda falhar no meio, o estoque NÃO é alterado!
```

---

## 🛡️ Segurança Implementada

- **CSRF Protection**: Token anti-falsificação em todos os formulários
- **Login obrigatório**: `@login_required` em todas as views sensíveis
- **Soft Delete**: Produtos não são apagados, só desativados (preserva histórico)
- **Validação**: Formulários Django validam dados antes de salvar
- **SECRET_KEY**: Via variável de ambiente, nunca no código

---

## 📈 Próximos Passos Sugeridos

1. **PostgreSQL em produção** — Troca SQLite por banco mais robusto
2. **Relatórios Excel** — Exportação com pandas/openpyxl
3. **Autenticação JWT** — Para API mobile (djangorestframework-simplejwt)
4. **Frontend React** — Consome a API REST já pronta
5. **Notificações** — Email quando estoque fica baixo
6. **Multi-loja** — Tenancy para múltiplas unidades

---

*Desenvolvido como sistema profissional full stack Python/Django*
