from django.urls import path
from . import views
app_name = 'caixa'
urlpatterns = [
    path('', views.lista_caixas, name='lista'),
    path('abrir/', views.abrir_caixa, name='abrir'),
    path('fechar/', views.fechar_caixa, name='fechar'),
    path('sangria/', views.sangria, name='sangria'),
]
