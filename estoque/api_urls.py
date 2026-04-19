"""
API URLs - Endpoints REST para o estoque
Permite que apps mobile, React, etc. usem os dados
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# 1. O GERADOR AUTOMÁTICO: O DefaultRouter é um "mago" das URLs.
# Ele olha para o seu ViewSet e cria sozinho as rotas de Listar, Criar, Deletar e Editar.
router = DefaultRouter()

# 2. REGISTRO: Aqui você define o "caminho principal" de cada coisa.
# 'produtos' vira /api/estoque/produtos/
# 'categorias' vira /api/estoque/categorias/
router.register('produtos', api_views.ProdutoViewSet, basename='produto')
router.register('categorias', api_views.CategoriaViewSet, basename='categoria')

# 3. O CAMINHO FINAL: Pega todos esses endereços que o mago criou
# e joga dentro do sistema de rotas do Django.
urlpatterns = [
    path('', include(router.urls))
]