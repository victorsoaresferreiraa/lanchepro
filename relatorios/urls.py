from django.urls import path
from . import views
app_name = 'relatorios'
urlpatterns = [
    path('', views.painel_relatorios, name='painel'),
    path('excel/', views.download_relatorio_excel, name='excel'),
    path('caixa/<int:caixa_id>/excel/', views.download_relatorio_caixa, name='caixa_excel'),
    path('api/grafico/', views.api_dados_grafico, name='grafico_api'),
]
