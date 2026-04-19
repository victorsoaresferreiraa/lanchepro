from django.urls import path
from . import views

# O 'app_name' é o apelido desse conjunto de rotas. 
# Quando você quiser ir para o PDV em qualquer lugar do código, 
# você chama 'vendas:pdv'. É como o sobrenome da família.
app_name = 'vendas'

urlpatterns = [
    # ROTA: A porta de entrada da loja (vazio '' significa a página inicial do app)
    # O que faz: Abre a tela do balcão (PDV)
    path('', views.pdv, name='pdv'),

    # ROTA: O botão de "Pagar" ou "Confirmar"
    # O que faz: Envia os dados do carrinho para o cérebro processar a venda
    path('finalizar/', views.finalizar_venda, name='finalizar'),

    # ROTA: A impressora de recibos
    # O que faz: Mostra o papelzinho da venda. 
    # O '<int:pk>' é o número da venda (ex: recibo/10/, recibo/11/)
    path('recibo/<int:pk>/', views.recibo, name='recibo'),

    # ROTA: O livro de contabilidade
    # O que faz: Abre a página com a lista de tudo que já foi vendido
    path('historico/', views.historico, name='historico'),
]