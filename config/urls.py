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
    # Painel admin do Django (automático e gratuito!)
    path('admin/', admin.site.urls),
    
    # Raiz do site → redireciona para dashboard
    path('', lambda req: redirect('/dashboard/')),
    
    # Login / Logout
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Apps do sistema
    path('dashboard/', include('dashboard.urls')),
    path('estoque/', include('estoque.urls')),
    path('vendas/', include('vendas.urls')),
    path('caixa/', include('caixa.urls')),
    path('clientes/', include('clientes.urls')),
    
    # API REST - Para quando quiser fazer app mobile ou frontend separado
    path('api/estoque/', include('estoque.api_urls')),
    path('api/vendas/', include('vendas.api_urls')),
    path('api/caixa/', include('caixa.api_urls')),
    path('api/clientes/', include('clientes.api_urls')),
    path('api/dashboard/', include('dashboard.api_urls')),
    path('relatorios/', include('relatorios.urls')),
]

# Em desenvolvimento, serve arquivos de mídia (fotos de produtos etc)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
