from django.urls import path
from . import views
app_name = 'vendas'
urlpatterns = [
    path('', views.pdv, name='pdv'),
    path('finalizar/', views.finalizar_venda, name='finalizar'),
    path('recibo/<int:pk>/', views.recibo, name='recibo'),
    path('historico/', views.historico, name='historico'),
]
