"""
API URLs - Endpoints REST para o estoque
Permite que apps mobile, React, etc. usem os dados
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register('produtos', api_views.ProdutoViewSet, basename='produto')
router.register('categorias', api_views.CategoriaViewSet, basename='categoria')

urlpatterns = [path('', include(router.urls))]
