from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# 1. O GERADOR DE ENDEREÇOS: O DefaultRouter é um "mago". 
# Em vez de você criar um endereço para "listar" e outro para "detalhes", 
# ele cria todos os caminhos padrão da API sozinho.
router = DefaultRouter()

# 2. REGISTRO: Aqui você diz para o mago: 
# "Toda vez que alguém chegar no endereço da API, mande para o VendaViewSet".
# O prefixo vazio '' significa que ele já começa na raiz da URL da API.
router.register('', api_views.VendaViewSet, basename='venda')

# 3. AS ROTAS: Aqui a gente inclui todos os caminhos que o mago criou 
# dentro da lista de URLs oficial do Django.
urlpatterns = [
    path('', include(router.urls))
]