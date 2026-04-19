from django.urls import path
from . import views

# O 'app_name' serve para você chamar as rotas no sistema como 'relatorios:painel'.
# É o sobrenome das rotas desta parte do sistema.
app_name = 'relatorios'

urlpatterns = [
    # ROTA: A porta de entrada do escritório do patrão.
    # O que faz: Abre a página bonita com os resumos, Top 5 e alertas.
    path('', views.painel_relatorios, name='painel'),

    # ROTA: O botão de "Baixar Planilha Geral".
    # O que faz: Gera o arquivo Excel com todas as vendas do período.
    path('excel/', views.download_relatorio_excel, name='excel'),

    # ROTA: O botão de "Baixar Planilha deste Caixa".
    # O que faz: O '<int:caixa_id>' é o número do caixa. 
    # Ex: /relatorios/caixa/5/excel/ baixa tudo o que aconteceu no caixa nº 5.
    path('caixa/<int:caixa_id>/excel/', views.download_relatorio_caixa, name='caixa_excel'),

    # ROTA: O túnel de dados para os gráficos.
    # O que faz: Essa rota não mostra uma página, ela entrega os números "crus" (JSON)
    # para o gráfico de linhas ou de barras ser desenhado na tela.
    path('api/grafico/', views.api_dados_grafico, name='grafico_api'),
]