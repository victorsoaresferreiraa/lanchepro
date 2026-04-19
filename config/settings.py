"""
settings.py — Configurações do LanchoPro
=========================================
Preparado para funcionar em desenvolvimento (local) E produção (Railway)
automaticamente, sem precisar mudar nada manualmente.
"""
from pathlib import Path
from decouple import config # Ajuda a esconder senhas em arquivos .env

# Onde o projeto mora no seu HD
BASE_DIR = Path(__file__).resolve().parent.parent

# CHAVE MESTRA: Nunca mostre isso para ninguém na internet!
SECRET_KEY = config('SECRET_KEY', default='django-dev-key-troca-em-producao-12345!')

# MODO DE ERRO: True mostra o erro detalhado (bom pra você), 
# False esconde o erro (obrigatório na internet para hackers não verem seu código).
DEBUG = config('DEBUG', default=True, cast=bool)

# ============================================================
# ALLOWED_HOSTS — O "Filtro de Linha"
# ============================================================
# Aqui você lista quais sites podem rodar esse sistema. 
# Se alguém tentar clonar seu site em outro domínio, o Django bloqueia.
_raw_hosts = config('ALLOWED_HOSTS', default='localhost,127.0.0.1')
ALLOWED_HOSTS = [h.strip() for h in _raw_hosts.split(',') if h.strip()]

# ============================================================
# CSRF_TRUSTED_ORIGINS — O "Segurança do Portão"
# ============================================================
# Correção para o erro 403: O Django exige saber de onde vem o formulário.
# Se você está no Railway (https), precisa listar o domínio aqui, 
# senão ele acha que é um ataque e bloqueia o botão de salvar.
_raw_csrf = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:8000,http://127.0.0.1:8000'
)
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _raw_csrf.split(',') if o.strip()]

# OS MÓDULOS: Tudo o que a gente documentou (estoque, vendas, etc) entra aqui.
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework', # Para a API
    'corsheaders',     # Para o app de celular conseguir conversar com o site
    'estoque',
    'vendas',
    'caixa',
    'clientes',
    'dashboard',
    'relatorios',
]

# MIDDLEWARE: Os "Seguranças" que ficam no corredor. 
# Cada um checa uma coisa (segurança, login, sessões) antes do pedido chegar na View.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Cuida do CSS/JS na nuvem
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls' # Onde está o mapa principal de estradas

# O VISUAL: Onde o Django deve procurar os arquivos HTML
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Pasta principal de HTMLs
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ============================================================
# BANCO DE DADOS — Onde a memória da loja fica guardada
# ============================================================
_db_url = config('DATABASE_URL', default='')

if _db_url:
    # Se estiver no Railway, usa o PostgreSQL (Robusto/Profissional)
    import dj_database_url
    DATABASES = {'default': dj_database_url.parse(_db_url, conn_max_age=600)}
else:
    # Se estiver no seu PC, usa o SQLite (Simples/Arquivo local)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'data' / 'lanchonete.db',
        }
    }

# LINGUAGEM E HORÁRIO: Deixa o sistema falando Brasileiro e com a hora de SP.
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# ============================================================
# ARQUIVOS ESTÁTICOS (CSS, JS) — A "Maquiagem" do site
# ============================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # Onde o servidor guarda a maquiagem pronta
STATICFILES_DIRS = [BASE_DIR / 'static']
# O WhiteNoise compacta o CSS para o site carregar mais rápido
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# MEDIA: Onde ficam as fotos dos produtos que você cadastrar
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CONFIGURAÇÕES DA API (REST FRAMEWORK)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated', # Só logado pode ver a API
    ],
    'PAGE_SIZE': 20, # Mostra 20 produtos por página na API
}

# REDIRECIONAMENTOS: Para onde o usuário vai ao logar ou sair.
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# ============================================================
# SEGURANÇA EM PRODUÇÃO (Cadeado Triplo)
# ============================================================
if not DEBUG:
    # Obriga o site a usar HTTPS (o cadeadinho verde no navegador)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True