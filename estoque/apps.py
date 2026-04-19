from django.apps import AppConfig

# Esta classe é a "identidade" do seu módulo de estoque dentro do projeto
class EstoqueConfig(AppConfig):
    # O nome da pasta onde estão os arquivos (models, views, etc.)
    name = 'estoque'
    
    # DICA DE MESTRE: É aqui que você poderia configurar um nome mais bonito
    # para aparecer no painel administrativo, tipo: verbose_name = 'Controle de Almoxarifado'