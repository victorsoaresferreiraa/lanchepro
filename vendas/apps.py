from django.apps import AppConfig

# Esta classe é a Certidão de Nascimento do seu app de vendas
class VendasConfig(AppConfig):
    # O nome oficial do aplicativo dentro do projeto
    name = 'vendas'
    
    # DICA: Geralmente o Django usa isso para configurar coisas que 
    # devem acontecer assim que o sistema liga (como sinais/signals).