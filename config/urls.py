"""
URLS PRINCIPAIS - O Mapa de rotas do sistema
Cada linha aqui é como uma placa de trânsito:
"Se o usuário acessar /estoque/ → vai para o app estoque"
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

urlpatterns = [
    # 1. A SALA DO CHEFE: O painel admin do Django.
    # Se você digitar /admin/, entra no sistema de gerenciamento padrão.
    path('admin/', admin.site.urls),
    
    # 2. O ATALHO: Se o usuário digitar só o site (vazio ''), 
    # ele é "empurrado" (redirect) direto para o dashboard.
    path('', lambda req: redirect('/dashboard/')),
    
    # 3. AS CHAVES DA PORTA: Telas de entrada (Login) e saída (Logout).
    # O Django já tem isso pronto, você só aponta onde está o seu desenho (template).
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # 4. OS SETORES DA EMPRESA: Aqui você conecta cada "puxadinho" (app) ao site principal.
    # O 'include' diz: "Se começar com /estoque/, passe a bola para o arquivo urls.py de dentro do app estoque".
    path('dashboard/', include('dashboard.urls')),
    path('estoque/', include('estoque.urls')),
    path('vendas/', include('vendas.urls')),
    path('caixa/', include('caixa.urls')),
    path('clientes/', include('clientes.urls')),
    path('relatorios/', include('relatorios.urls')),
    
    # 5. O GUICHÊ DE DADOS (API): Rotas especiais para o aplicativo de celular ou sistemas externos.
    # É por aqui que os dados "limpos" (JSON) viajam.
    path('api/estoque/', include('estoque.api_urls')),
    path('api/vendas/', include('vendas.api_urls')),
    path('api/caixa/', include('caixa.api_urls')),
    path('api/clientes/', include('clientes.api_urls')),
    path('api/dashboard/', include('dashboard.api_urls')),
]

# 6. MODO CONSTRUÇÃO (DEBUG):
# Enquanto você está desenvolvendo no seu PC, o Django precisa de uma ajuda
# extra para mostrar fotos de produtos e arquivos de estilo (CSS/JS).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)