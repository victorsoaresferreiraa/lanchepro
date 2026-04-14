#!/bin/sh
# ============================================================
# ENTRYPOINT — Roda ao iniciar o container
# ============================================================
# Este script roda SEMPRE que o container sobe.
# Garante que o banco está atualizado antes de iniciar o servidor.

set -e  # Para na primeira falha

echo "🍔 LanchoPro iniciando..."

# Aplica migrations automaticamente
echo "📦 Aplicando migrations..."
python manage.py migrate --noinput

# Cria superusuário se não existir (via variáveis de ambiente)
echo "👤 Verificando usuário admin..."
python manage.py shell -c "
from django.contrib.auth.models import User
import os
if not User.objects.filter(username=os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')).exists():
    User.objects.create_superuser(
        username=os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin'),
        password=os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123'),
        email=os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@lanchopro.com'),
    )
    print('✅ Superusuário criado')
else:
    print('ℹ️  Superusuário já existe')
"

# Popula dados iniciais se banco estiver vazio
python manage.py shell -c "
from estoque.models import Produto
if Produto.objects.count() == 0:
    import subprocess
    subprocess.run(['python', 'manage.py', 'seed_data'])
"

echo "🚀 Iniciando servidor Gunicorn..."
# Gunicorn = servidor WSGI profissional
# -w 2 = 2 workers (processos paralelos)
# --bind 0.0.0.0:8000 = aceita conexões de qualquer IP na porta 8000
# config.wsgi = nosso arquivo wsgi.py
exec gunicorn config.wsgi:application \
    --workers 2 \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
