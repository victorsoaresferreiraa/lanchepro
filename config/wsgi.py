"""
WSGI config for config project.

Ele expõe o "aplicativo" para o servidor web.
É o ponto de entrada para o servidor de produção (onde o site mora de verdade).
"""

import os

from django.core.wsgi import get_wsgi_application

# 1. ENDEREÇO DA CONFIGURAÇÃO: 
# Diz para o servidor: "Ó, as regras de como esse site funciona (banco de dados, apps, etc) 
# estão guardadas lá no arquivo config/settings.py".
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 2. O APLICATIVO EM SI:
# Aqui o Django cria o objeto 'application'. Quando alguém acessa seu site, 
# o servidor chama essa variável para saber o que responder.
application = get_wsgi_application()