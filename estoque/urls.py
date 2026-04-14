from django.urls import path
from . import views

app_name = 'estoque'

urlpatterns = [
    path('', views.lista_produtos, name='lista'),
    path('novo/', views.criar_produto, name='criar'),
    path('<int:pk>/editar/', views.editar_produto, name='editar'),
    path('<int:pk>/excluir/', views.excluir_produto, name='excluir'),
    path('<int:pk>/ajustar/', views.ajustar_estoque, name='ajustar'),
]
