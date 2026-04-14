# ============================================================
# DOCKERFILE — LanchoPro
# ============================================================
# O que é um Dockerfile?
# É a "receita" para montar um container Docker.
# Docker cria um ambiente isolado e idêntico em qualquer máquina.
# Assim: funciona no seu PC → funciona no servidor → funciona em qualquer lugar!
#
# FLUXO:
# 1. Começa com uma imagem Python 3.12 já pronta
# 2. Instala nossas dependências (requirements.txt)
# 3. Copia o código
# 4. Roda as migrations
# 5. Inicia o servidor Gunicorn (servidor web profissional)
# ============================================================

# Imagem base: Python 3.12 slim (versão enxuta)
FROM python:3.12-slim

# Não gera arquivos .pyc desnecessários
ENV PYTHONDONTWRITEBYTECODE=1
# Logs aparecem imediatamente (sem buffer)
ENV PYTHONUNBUFFERED=1

# Pasta de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema operacional
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python primeiro
# (Docker faz cache desta camada — se requirements.txt não mudar, reaproveita)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do projeto
COPY . .

# Cria as pastas necessárias
RUN mkdir -p data staticfiles media

# Coleta todos os arquivos estáticos em staticfiles/
# (WhiteNoise os serve diretamente sem precisar de Nginx)
RUN python manage.py collectstatic --noinput

# Porta que o container vai expor
EXPOSE 8000

# Script de inicialização
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Comando que roda ao iniciar o container
ENTRYPOINT ["/docker-entrypoint.sh"]
