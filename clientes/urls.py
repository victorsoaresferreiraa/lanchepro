from django.urls import path
from . import views
app_name = 'clientes'
urlpatterns = [
    path('', views.lista_clientes, name='lista'),
    path('<int:pk>/', views.detalhe_cliente, name='detalhe'),
    path('nova-conta/', views.criar_conta_aberta, name='nova_conta'),
    path('conta/<int:pk>/pagar/', views.registrar_pagamento, name='pagar'),
]
